import os
import json
from datasets import load_dataset
import tiktoken

os.makedirs("data/chunks", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("Downloading PubMed QA dataset...")
ds_labeled = load_dataset("pubmed_qa", "pqa_labeled", split="train")
ds_unlabeled = load_dataset("pubmed_qa", "pqa_unlabeled", split="train")

chunks = []
qa_pairs = []

# Process labeled split (has gold answers)
print("Processing labeled split ...")
for i, item in enumerate(ds_labeled):
    for j, ctx in enumerate(item["context"]["contexts"]):
        words = ctx.split()
        for k in range(0, len(words), 300):
            chunk_text = " ".join(words[k : k + 300])
            if len(chunk_text.strip()) > 50:
                chunks.append(
                    {
                        "id": f"lbl_{i}_{j}_{k}",
                        "text": chunk_text,
                        "source": "pubmed_qa_labeled",
                    }
                )

    qa_pairs.append(
        {
            "id": i,
            "question": item["question"],
            "gold_answer": item["long_answer"],
            "label": item["final_decision"],
        }
    )

print(f"  Labeled split: {len(chunks):,} chunks, {len(qa_pairs)} QA pairs")

# Process unlabeled split to hit 2M token target
print("Processing unlabeled split ...")
for i, item in enumerate(ds_unlabeled):
    for j, ctx in enumerate(item["context"]["contexts"]):
        words = ctx.split()
        for k in range(0, len(words), 300):
            chunk_text = " ".join(words[k : k + 300])
            if len(chunk_text.strip()) > 50:
                chunks.append(
                    {
                        "id": f"unlbl_{i}_{j}_{k}",
                        "text": chunk_text,
                        "source": "pubmed_qa_unlabeled",
                    }
                )

# Count tokens
enc = tiktoken.get_encoding("cl100k_base")
total_tokens = sum(len(enc.encode(c["text"])) for c in chunks)
print(f"\nTotal chunks: {len(chunks):,}")
print(f"Total tokens: {total_tokens:,}")

if total_tokens < 2_000_000:
    print("⚠️  WARNING: Under 2M tokens. Consider adding more data sources.")
else:
    print("✅ Token target met (2M+)")

# Save chunks
with open("data/chunks/chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f)
print(f"Saved {len(chunks):,} chunks to data/chunks/chunks.json")

# Save QA pairs (first 50 for benchmarking)
with open("data/qa_pairs.json", "w", encoding="utf-8") as f:
    json.dump(qa_pairs[:50], f, indent=2)
print(f"Saved {len(qa_pairs[:50])} QA pairs to data/qa_pairs.json")
