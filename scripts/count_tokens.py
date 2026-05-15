import tiktoken
import json

enc = tiktoken.get_encoding("cl100k_base")

with open("data/chunks/chunks.json", encoding="utf-8") as f:
    chunks = json.load(f)

total_tokens = 0

for c in chunks:
    total_tokens += len(enc.encode(c["text"]))

print(f"Total tokens: {total_tokens:,}")