from datasets import load_dataset
import json
import os

print("Starting script...")

os.makedirs("data/chunks", exist_ok=True)

chunks = []
qa_pairs = []

# -----------------------------
# LABELED DATA
# -----------------------------
print("Loading labeled dataset...")

labeled_ds = load_dataset(
    "pubmed_qa",
    "pqa_labeled",
    split="train"
)

print(f"Labeled samples: {len(labeled_ds)}")

for i, item in enumerate(labeled_ds):

    contexts = item["context"]["contexts"]

    for j, ctx in enumerate(contexts):

        chunks.append({
            "id": f"labeled_{i}_{j}",
            "text": ctx,
            "source_question": item["question"]
        })

    qa_pairs.append({
        "id": i,
        "question": item["question"],
        "gold_answer": item["long_answer"],
        "label": item["final_decision"]
    })

# -----------------------------
# UNLABELED DATA
# -----------------------------
print("Loading unlabeled dataset...")

unlabeled_ds = load_dataset(
    "pubmed_qa",
    "pqa_unlabeled",
    split="train"
)

print(f"Unlabeled samples: {len(unlabeled_ds)}")

for i, item in enumerate(unlabeled_ds):

    contexts = item["context"]["contexts"]

    for j, ctx in enumerate(contexts):

        chunks.append({
            "id": f"unlabeled_{i}_{j}",
            "text": ctx,
            "source_question": item["question"]
        })

print("Saving files...")

# Save chunks
with open("data/chunks/chunks.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f, indent=2)

# Save QA benchmark set
with open("data/qa_pairs.json", "w", encoding="utf-8") as f:
    json.dump(qa_pairs[:50], f, indent=2)

print(f"Total chunks: {len(chunks)}")
print(f"QA pairs saved: {len(qa_pairs[:50])}")

print("DONE")