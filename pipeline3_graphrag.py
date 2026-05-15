"""
Pipeline 3 — GraphRAG via TigerGraph Cloud (native REST++ implementation)

The TigerGraph Cloud instance is the DATABASE only — the separate GraphRAG
FastAPI container is not deployed there.  This file implements GraphRAG
manually using pyTigerGraph + TigerGraph REST++ directly:

  Schema:  Chunk vertex, Entity vertex, MENTIONS edge (Chunk→Entity),
           RELATED edge (Entity→Entity)
  Ingest:  chunks become Chunk vertices; Gemini extracts entities
           from each chunk and creates Entity vertices + MENTIONS edges
  Query:   embed question → find top-k matching Chunks (keyword fallback)
           → 2-hop graph traversal to collect related Chunks via shared
           Entities → Gemini generates final answer from expanded context

Run modes:
  python pipeline3_graphrag.py check   — verify TG connection & auth
  python pipeline3_graphrag.py init    — create graph + schema
  python pipeline3_graphrag.py ingest  — load chunks (default: 200)
  python pipeline3_graphrag.py ingest 500 — load 500 chunks
  (no args)                            — run a test query
"""

import sys
import time
import json, time
import os
import requests
import tiktoken
from google import genai

from config import (MODEL,
    GRAPHRAG_BASE_URL,
    GRAPHRAG_USERNAME,
    GRAPHRAG_PASSWORD,
    GRAPHRAG_GRAPH_NAME,
    GEMINI_API_KEY,
    PRICE_INPUT,
    PRICE_OUTPUT,
)

enc = tiktoken.get_encoding("cl100k_base")
_gemini_client = genai.Client(api_key=GEMINI_API_KEY)



def generate_with_retry(prompt, model=MODEL, max_retries=5):
    for i in range(max_retries):
        try:
            return _gemini_client.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "500" in err_str or "UNAVAILABLE" in err_str) and i < max_retries - 1:
                wait = (2 ** i) + 15
                print(f"Server error or Rate limit. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e

HOST = GRAPHRAG_BASE_URL.rstrip("/")
GRAPH = GRAPHRAG_GRAPH_NAME

# ─── Auth helpers ─────────────────────────────────────────────────────────────

_token: str | None = None


def _get_token() -> str:
    """Get (and cache) a TigerGraph REST++ auth token."""
    global _token
    if _token:
        return _token

    try:
        from pyTigerGraph import TigerGraphConnection

        conn = TigerGraphConnection(
            host=HOST,
            graphname=GRAPH,
            username=GRAPHRAG_USERNAME,
            password=GRAPHRAG_PASSWORD,
            restppPort="443",
            gsPort="443",
        )
        # createSecret needs GSQL access; if it fails we try the REST endpoint
        try:
            secret = conn.createSecret()
            tok = conn.getToken(secret)[0]
            _token = tok
            return _token
        except Exception:
            pass
    except ImportError:
        pass

    # Fallback: direct REST++ token request
    for path in ["/restpp/requesttoken", "/api/requesttoken"]:
        try:
            r = requests.post(
                f"{HOST}{path}",
                auth=(GRAPHRAG_USERNAME, GRAPHRAG_PASSWORD),
                json={"secret": GRAPHRAG_PASSWORD, "lifetime": "86400"},
                timeout=15,
                verify=True,
            )
            if r.ok:
                data = r.json()
                tok = (
                    data.get("results", {}).get("token")
                    or data.get("token")
                )
                if tok:
                    _token = tok
                    return _token
        except Exception:
            pass

    raise RuntimeError(
        "Cannot obtain TigerGraph auth token.\n"
        "Make sure GRAPHRAG_USERNAME / GRAPHRAG_PASSWORD are correct\n"
        "and that your TigerGraph instance is running."
    )


def _headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}",
            "Content-Type": "application/json"}


def _restpp(method: str, path: str, **kwargs):
    """Thin wrapper around requests for REST++ calls."""
    url = f"{HOST}/restpp{path}"
    return requests.request(method, url, headers=_headers(), timeout=60, **kwargs)


# ─── Endpoint / connection check ──────────────────────────────────────────────

def check_api_endpoints():
    print(f"Target: {HOST}")
    print(f"Graph:  {GRAPH}\n")

    # 1. No-auth probes
    for path in ["/restpp/version", "/restpp/echo", f"/restpp/graph/{GRAPH}"]:
        try:
            r = requests.get(f"{HOST}{path}", timeout=10, verify=True)
            print(f"  GET {path}: HTTP {r.status_code}")
            if r.ok:
                print(f"    {r.text[:120]}")
        except Exception as e:
            print(f"  GET {path}: ERROR — {e}")

    # 2. Auth token
    print()
    try:
        tok = _get_token()
        print(f"  Token obtained: {tok[:20]}…")
    except Exception as e:
        print(f"  Token ERROR: {e}")
        return

    # 3. Authed probes
    for path in [
        f"/graph/{GRAPH}/vertices/Chunk",
        f"/graph/{GRAPH}/vertices/Entity",
    ]:
        try:
            r = _restpp("GET", path)
            print(f"  GET /restpp{path}: HTTP {r.status_code}")
            if r.ok:
                print(f"    {r.text[:120]}")
        except Exception as e:
            print(f"  /restpp{path}: ERROR — {e}")


# ─── Schema / graph init ──────────────────────────────────────────────────────

_SCHEMA_GSQL = f"""
USE GLOBAL
CREATE VERTEX Chunk (
  PRIMARY_ID chunk_id STRING,
  text STRING,
  source STRING
) WITH primary_id_as_attribute="true"

CREATE VERTEX Entity (
  PRIMARY_ID entity_id STRING,
  name STRING,
  entity_type STRING
) WITH primary_id_as_attribute="true"

CREATE UNDIRECTED EDGE MENTIONS (FROM Chunk, TO Entity)
CREATE UNDIRECTED EDGE RELATED  (FROM Entity, TO Entity)

CREATE GRAPH {GRAPH} (Chunk, Entity, MENTIONS, RELATED)
"""


def init_graph():
    """Create graph and schema via GSQL REST endpoint."""
    print(f"Initialising graph '{GRAPH}' …")
    tok = _get_token()

    gsql_endpoints = [
        "/gsqlserver/gsql/file",
        "/gsql/v1/statements",
        "/gsql",
    ]

    for ep in gsql_endpoints:
        try:
            r = requests.post(
                f"{HOST}{ep}",
                headers={"Authorization": f"Bearer {tok}", "Content-Type": "text/plain"},
                data=_SCHEMA_GSQL,
                timeout=120,
                verify=True,
            )
            print(f"  {ep}: HTTP {r.status_code} — {r.text[:200]}")
            if r.status_code in [200, 201]:
                print("  Schema created.")
                return True
        except Exception as e:
            print(f"  {ep}: ERROR — {e}")

    print(
        "\nIf schema creation failed, create the graph manually in TigerGraph Studio:\n"
        f"  1. Log in at {HOST}\n"
        f"  2. Create a new graph named '{GRAPH}'\n"
        "  3. Add vertex types: Chunk (content STRING, source STRING)\n"
        "              Entity (name STRING, entity_type STRING)\n"
        "  4. Add edge types: MENTIONS (Chunk→Entity), RELATED (Entity→Entity)\n"
    )
    return False


# ─── Ingest helpers ───────────────────────────────────────────────────────────

def _extract_entities(text: str) -> list[str]:
    """Ask Gemini to extract up to 5 biomedical entities from a chunk."""
    try:
        resp = generate_with_retry(
            prompt=(
                f"List up to 5 key biomedical entities (drugs, diseases, genes, "
                f"proteins) from this text as a JSON array of strings. "
                f"Return ONLY the JSON array.\n\nText:\n{text[:800]}"
            ),
        )
        raw = resp.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1].lstrip("json").strip()
        return json.loads(raw)
    except Exception:
        return []


def ingest_documents(chunks: list, limit: int = 200):
    """Ingest chunks into TigerGraph as Chunk + Entity vertices with edges."""
    target = chunks[:limit]
    print(f"Ingesting {len(target)} chunks into '{GRAPH}' …")

    chunk_ok = entity_ok = edge_ok = 0

    for i, chunk in enumerate(target):
        cid = str(chunk["id"])
        text = chunk["text"]
        source = chunk.get("source", "pubmed_qa")

        # --- Upsert Chunk vertex ---
        payload = {
            "vertices": {
                "Chunk": {
                    cid: {
                        "text": {"value": text},
                        "source":  {"value": source},
                    }
                }
            }
        }
        r = _restpp("POST", f"/graph/{GRAPH}", json=payload)
        if r.ok:
            chunk_ok += 1

        # --- Extract entities + upsert ---
        if i < 50:          # Only extract for first 50 to keep costs low
            entities = _extract_entities(text)
            edge_list = []
            for ent in entities:
                eid = ent.lower().replace(" ", "_")[:64]
                ep = {
                    "vertices": {
                        "Entity": {
                            eid: {
                                "name":        {"value": ent},
                                "entity_type": {"value": "biomedical"},
                            }
                        }
                    },
                    "edges": {
                        "Chunk": {
                            cid: {
                                "MENTIONS": {
                                    "Entity": {eid: {}}
                                }
                            }
                        }
                    },
                }
                re = _restpp("POST", f"/graph/{GRAPH}", json=ep)
                if re.ok:
                    entity_ok += 1

        if (i + 1) % 20 == 0:
            pct = (i + 1) / len(target) * 100
            print(f"  [{pct:5.1f}%] {i+1}/{len(target)} — "
                  f"chunks:{chunk_ok} entities:{entity_ok}")
        time.sleep(0.1)

    print(f"\n  Ingested: {chunk_ok} chunks, {entity_ok} entities")
    return chunk_ok > 0


# ─── Query (Pipeline 3) ────────────────────────────────────────────────────────

def _search_chunks(question: str, top_k: int = 5) -> list[str]:
    """
    Retrieve relevant chunks via TigerGraph:
      Step 1 — keyword search: find Chunks whose content contains query words
      Step 2 — graph hop: for those Chunks, find shared Entities,
                          then expand to other Chunks mentioning same Entities
    Returns a deduplicated list of content strings.
    """
    words = [w for w in question.lower().split() if len(w) > 4][:6]

    # REST++ built-in: filter vertices by attribute string-contains
    found_ids: list[str] = []
    for word in words[:3]:
        try:
            r = _restpp(
                "GET",
                f"/graph/{GRAPH}/vertices/Chunk",
                params={"filter": f"text LIKE '%{word}%'", "limit": top_k},
            )
            if r.ok:
                results = r.json().get("results", [])
                for v in results:
                    found_ids.append(v.get("v_id", ""))
        except Exception:
            pass

    found_ids = list(dict.fromkeys(found_ids))  # deduplicate, keep order

    # 2-hop expansion via MENTIONS edges
    expanded_ids: list[str] = list(found_ids)
    for cid in found_ids[:3]:
        try:
            # Get entities mentioned in this chunk
            r = _restpp(
                "GET",
                f"/graph/{GRAPH}/edges/Chunk/{cid}/MENTIONS/Entity",
            )
            if r.ok:
                for e in r.json().get("results", []):
                    eid = e.get("to_id", "")
                    if not eid:
                        continue
                    # Get other chunks mentioning the same entity
                    r2 = _restpp(
                        "GET",
                        f"/graph/{GRAPH}/edges/Entity/{eid}/MENTIONS/Chunk",
                    )
                    if r2.ok:
                        for e2 in r2.json().get("results", []):
                            expanded_ids.append(e2.get("to_id", ""))
        except Exception:
            pass

    expanded_ids = list(dict.fromkeys(expanded_ids))[:top_k]

    # Fetch text for the collected chunk IDs
    contents: list[str] = []
    for cid in expanded_ids:
        try:
            r = _restpp("GET", f"/graph/{GRAPH}/vertices/Chunk/{cid}")
            if r.ok:
                attrs = r.json().get("results", [{}])[0].get("attributes", {})
                txt = attrs.get("text", "")
                if txt:
                    contents.append(txt)
        except Exception:
            pass

    return contents[:top_k]


def run_pipeline3(question: str) -> dict:
    """GraphRAG: multi-hop TigerGraph retrieval → Gemini answer."""
    start = time.time()

    try:
        context_chunks = _search_chunks(question, top_k=4)
    except Exception as e:
        context_chunks = []
        print(f"  TG retrieval error: {e}")

    context = "\n\n---\n\n".join(context_chunks) if context_chunks else ""

    if context:
        prompt = (
            "You are a biomedical expert. Answer using ONLY the graph-retrieved context.\n\n"
            f"Context (multi-hop graph retrieval):\n{context}\n\n"
            f"Question: {question}\n\nAnswer:"
        )
    else:
        # Graceful fallback: answer without context (treated like pipeline1)
        prompt = (
            "You are a biomedical expert. Answer concisely.\n\n"
            f"Question: {question}\n\nAnswer:"
        )

    response = generate_with_retry(prompt)
    latency = time.time() - start

    p_tokens = response.usage_metadata.prompt_token_count
    c_tokens = response.usage_metadata.candidates_token_count

    return {
        "pipeline": "GraphRAG",
        "answer": response.text,
        "prompt_tokens": p_tokens,
        "completion_tokens": c_tokens,
        "total_tokens": p_tokens + c_tokens,
        "latency_seconds": round(latency, 3),
        "cost_usd": round(p_tokens * PRICE_INPUT + c_tokens * PRICE_OUTPUT, 8),
        "context_chunks": len(context_chunks),
    }


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "query"

    if mode == "check":
        check_api_endpoints()

    elif mode == "init":
        init_graph()

    elif mode == "ingest":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 200
        with open("data/chunks/chunks.json", encoding="utf-8") as f:
            chunks = json.load(f)
        ingest_documents(chunks, limit=limit)

    else:
        result = run_pipeline3("Does aspirin reduce platelet aggregation?")
        print(json.dumps(result, indent=2))


