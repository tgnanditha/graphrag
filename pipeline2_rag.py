import chromadb
import time
import json, time
from google import genai
from sentence_transformers import SentenceTransformer
from config import MODEL, GEMINI_API_KEY, PRICE_INPUT, PRICE_OUTPUT, CHROMA_PATH

_gemini = genai.Client(api_key=GEMINI_API_KEY)

embedder = SentenceTransformer("all-MiniLM-L6-v2")


def generate_with_retry(prompt, model=MODEL, max_retries=5):
    for i in range(max_retries):
        try:
            return _gemini.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "500" in err_str or "UNAVAILABLE" in err_str) and i < max_retries - 1:
                wait = (2 ** i) + 15
                print(f"Server error or Rate limit. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = _client.get_collection("pubmed")
    return _collection


def run_pipeline2(question: str, top_k: int = 5) -> dict:
    """Retrieve top-k similar chunks via vector search, then answer with Gemini."""
    start = time.time()

    collection = get_collection()
    q_embed = embedder.encode([question]).tolist()
    results = collection.query(query_embeddings=q_embed, n_results=top_k)
    context_chunks = results["documents"][0]
    context = "\n\n---\n\n".join(context_chunks)

    prompt = f"""You are a biomedical expert. Answer the question using ONLY the provided context.
If the context does not contain enough information, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    response = generate_with_retry(prompt)
    latency = time.time() - start

    p_tokens = response.usage_metadata.prompt_token_count
    c_tokens = response.usage_metadata.candidates_token_count

    return {
        "pipeline": "Basic-RAG",
        "answer": response.text,
        "prompt_tokens": p_tokens,
        "completion_tokens": c_tokens,
        "total_tokens": p_tokens + c_tokens,
        "latency_seconds": round(latency, 3),
        "cost_usd": round(p_tokens * PRICE_INPUT + c_tokens * PRICE_OUTPUT, 8),
        "context_chunks": top_k,
    }


if __name__ == "__main__":
    result = run_pipeline2("Does aspirin reduce platelet aggregation?")
    print(json.dumps(result, indent=2))


