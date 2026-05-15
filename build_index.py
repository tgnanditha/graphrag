import chromadb
import json
import os
from sentence_transformers import SentenceTransformer
from config import CHROMA_PATH, CHUNKS_PATH

print("Loading chunks...")
with open(CHUNKS_PATH, encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks):,} chunks")
print("Loading embedding model (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=CHROMA_PATH)

# Delete existing collection if rebuilding
try:
    client.delete_collection("pubmed")
    print("Deleted existing collection — rebuilding from scratch")
except Exception:
    pass

collection = client.create_collection(
    "pubmed",
    metadata={"hnsw:space": "cosine"},
)

BATCH_SIZE = 500
texts = [c["text"] for c in chunks]
ids = [str(c["id"]) for c in chunks]

print(f"Indexing {len(texts):,} chunks in batches of {BATCH_SIZE}...")
for i in range(0, len(texts), BATCH_SIZE):
    batch_texts = texts[i : i + BATCH_SIZE]
    batch_ids = ids[i : i + BATCH_SIZE]
    batch_embeds = embedder.encode(
        batch_texts,
        show_progress_bar=False,
        batch_size=64,
    ).tolist()
    collection.add(
        documents=batch_texts,
        ids=batch_ids,
        embeddings=batch_embeds,
    )
    done = min(i + BATCH_SIZE, len(texts))
    pct = done / len(texts) * 100
    print(f"  [{pct:5.1f}%] Indexed {done:,}/{len(texts):,} chunks")

print(f"\n✅ Index complete. Saved to {CHROMA_PATH}")
print(f"   Collection size: {collection.count():,} documents")
