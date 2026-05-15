from google import genai
import json, time
import os
from bert_score import score as bert_score_fn
from config import MODEL, GEMINI_API_KEY, BENCHMARK_PATH, EVAL_SUMMARY_PATH, QA_PAIRS_PATH

_judge_client = genai.Client(api_key=GEMINI_API_KEY)



def generate_with_retry(prompt, model=MODEL, max_retries=5):
    for i in range(max_retries):
        try:
            return _judge_client.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "500" in err_str or "INTERNAL" in err_str or "UNAVAILABLE" in err_str) and i < max_retries - 1:
                wait = (2 ** i) + 10
                print(f"Retrying due to server load/rate limit ({err_str[:50]}...). Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e


def llm_judge(predicted: str, reference: str, question: str) -> str:
    """Use Gemini as LLM judge. Returns PASS or FAIL."""
    prompt = f"""You are an expert biomedical evaluator.

Question: {question}
Reference answer: {reference}
System answer: {predicted}

Does the system answer correctly and completely address the question, consistent with the reference answer?
Reply with ONLY one word: PASS or FAIL."""

    response = generate_with_retry(prompt)
    text = response.text.strip().upper()
    return "PASS" if "PASS" in text else "FAIL"


def compute_bertscore(predicted: str, reference: str) -> float:
    """Compute BERTScore F1. Bonus threshold: rescaled F1 >= 0.55."""
    P, R, F1 = bert_score_fn(
        [predicted],
        [reference],
        lang="en",
        model_type="distilbert-base-uncased",
        verbose=False,
    )
    return float(F1[0])


def evaluate_answer(predicted: str, reference: str, question: str = "") -> dict:
    """Full evaluation: LLM judge + BERTScore."""
    if not reference or not predicted:
        return {
            "llm_judge": "N/A",
            "bertscore_f1": 0.0,
            "bertscore_pass": False,
            "llm_judge_pass": False,
        }

    bertscore = compute_bertscore(predicted, reference)
    verdict = llm_judge(predicted, reference, question)

    return {
        "llm_judge": verdict,
        "bertscore_f1": round(bertscore, 4),
        "bertscore_pass": bertscore >= 0.55,
        "llm_judge_pass": verdict == "PASS",
    }


def run_full_benchmark_evaluation():
    """Evaluate all 3 pipelines across all benchmark results. Saves eval_summary.json."""
    with open(QA_PAIRS_PATH, encoding="utf-8") as f:
        qa_pairs = json.load(f)
    with open(BENCHMARK_PATH, encoding="utf-8") as f:
        benchmark = json.load(f)

    gold_lookup = {item["question"]: item["gold_answer"] for item in qa_pairs}

    eval_results = {
        "pipeline1": {"judges": [], "bertscores": []},
        "pipeline2": {"judges": [], "bertscores": []},
        "pipeline3": {"judges": [], "bertscores": []},
    }

    print(f"Evaluating {len(benchmark)} benchmark entries (first 20 only) ...")

    for i, entry in enumerate(benchmark[:20]):
        q = entry["question"]
        gold = gold_lookup.get(q, "")
        if not gold:
            continue

        for pipe_key in ["pipeline1", "pipeline2", "pipeline3"]:
            if pipe_key in entry.get("results", {}):
                answer = entry["results"][pipe_key].get("answer", "")
                if answer and "[API ERROR" not in answer:
                    scores = evaluate_answer(answer, gold, q)
                    eval_results[pipe_key]["judges"].append(scores["llm_judge_pass"])
                    eval_results[pipe_key]["bertscores"].append(scores["bertscore_f1"])

        print(f"  Evaluated {i + 1}/20")

    summary = {}
    for pipe_key, data in eval_results.items():
        if data["judges"]:
            pass_rate = sum(data["judges"]) / len(data["judges"])
            avg_bert = sum(data["bertscores"]) / len(data["bertscores"])
            summary[pipe_key] = {
                "llm_judge_pass_rate": round(pass_rate, 3),
                "avg_bertscore_f1": round(avg_bert, 4),
                "n_evaluated": len(data["judges"]),
                "meets_judge_bonus": pass_rate >= 0.90,
                "meets_bert_bonus": avg_bert >= 0.55,
            }

    os.makedirs("results", exist_ok=True)
    with open(EVAL_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n=== EVALUATION SUMMARY ===")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    run_full_benchmark_evaluation()
