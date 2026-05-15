import json
import os
import time
from datetime import datetime
from config import QA_PAIRS_PATH, BENCHMARK_PATH
from pipeline1_llm import run_pipeline1
from pipeline2_rag import run_pipeline2
from pipeline3_graphrag import run_pipeline3


def run_single_question(qa_item: dict) -> dict:
    """Run all 3 pipelines for one question. Returns full result entry."""
    q = qa_item["question"]
    gold = qa_item.get("gold_answer", "")

    print(f"\nQ: {q[:80]}...")

    results = {}
    for name, fn in [
        ("pipeline1", run_pipeline1),
        ("pipeline2", run_pipeline2),
        ("pipeline3", run_pipeline3),
    ]:
        try:
            results[name] = fn(q)
            tokens = results[name]["total_tokens"]
            latency = results[name]["latency_seconds"]
            print(f"  {name}: {tokens:,} tokens, {latency:.1f}s")
        except Exception as e:
            print(f"  {name}: ERROR — {e}")
            results[name] = {
                "error": str(e),
                "answer": "",
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "latency_seconds": 0,
                "cost_usd": 0,
            }

    # Report token delta
    p2_tokens = results.get("pipeline2", {}).get("total_tokens", 0)
    p3_tokens = results.get("pipeline3", {}).get("total_tokens", 0)
    if p2_tokens > 0 and p3_tokens > 0:
        reduction = (1 - p3_tokens / p2_tokens) * 100
        sign = "v" if reduction > 0 else "^"
        print(f"  GraphRAG vs RAG: {sign}{abs(reduction):.1f}% tokens")

    return {
        "timestamp": datetime.now().isoformat(),
        "question": q,
        "gold_answer": gold,
        "results": results,
    }


def main():
    with open(QA_PAIRS_PATH, encoding="utf-8") as f:
        qa_pairs = json.load(f)[:20]

    print(f"Running benchmark on {len(qa_pairs)} questions ...")
    os.makedirs("results", exist_ok=True)

    benchmark_results = []
    for i, qa in enumerate(qa_pairs):
        print(f"\n[{i + 1}/{len(qa_pairs)}]", end="")
        entry = run_single_question(qa)
        benchmark_results.append(entry)

        # Crash-safe incremental save
        with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
            json.dump(benchmark_results, f, indent=2)

        time.sleep(1)  # gentle rate-limit

    # Summary
    def avg_tok(key):
        vals = [e["results"].get(key, {}).get("total_tokens", 0) for e in benchmark_results]
        non_zero = [v for v in vals if v]
        return sum(non_zero) / len(non_zero) if non_zero else 0

    p1_avg = avg_tok("pipeline1")
    p2_avg = avg_tok("pipeline2")
    p3_avg = avg_tok("pipeline3")

    print(f"\n{'='*50}")
    print("BENCHMARK COMPLETE")
    print(f"{'='*50}")
    print(f"Avg tokens — LLM Only : {p1_avg:,.0f}")
    print(f"Avg tokens — Basic RAG: {p2_avg:,.0f}")
    print(f"Avg tokens — GraphRAG : {p3_avg:,.0f}")
    if p2_avg > 0 and p3_avg > 0:
        reduction = (1 - p3_avg / p2_avg) * 100
        print(f"GraphRAG token reduction vs Basic RAG: {reduction:.1f}%")
    print(f"Results saved to {BENCHMARK_PATH}")


if __name__ == "__main__":
    main()
