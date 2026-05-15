from google import genai
import time, json
from config import MODEL, GEMINI_API_KEY, PRICE_INPUT, PRICE_OUTPUT

_client = genai.Client(api_key=GEMINI_API_KEY)



def generate_with_retry(prompt, model=MODEL, max_retries=5):
    for i in range(max_retries):
        try:
            return _client.models.generate_content(model=model, contents=prompt)
        except Exception as e:
            
            err_str = str(e)
            if ("429" in err_str or "503" in err_str or "500" in err_str or "UNAVAILABLE" in err_str) and i < max_retries - 1:
                wait = (2 ** i) + 15
                print(f"Server error or Rate limit. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise e


def run_pipeline1(question: str) -> dict:
    """Send question to Gemini with zero context. Baseline."""
    start = time.time()

    prompt = f"""You are a biomedical expert. Answer this question concisely and accurately.

Question: {question}

Answer:"""

    response = generate_with_retry(prompt)
    latency = time.time() - start

    p_tokens = response.usage_metadata.prompt_token_count
    c_tokens = response.usage_metadata.candidates_token_count

    return {
        "pipeline": "LLM-Only",
        "answer": response.text,
        "prompt_tokens": p_tokens,
        "completion_tokens": c_tokens,
        "total_tokens": p_tokens + c_tokens,
        "latency_seconds": round(latency, 3),
        "cost_usd": round(p_tokens * PRICE_INPUT + c_tokens * PRICE_OUTPUT, 8),
        "context_chunks": 0,
    }


if __name__ == "__main__":
    result = run_pipeline1("Does aspirin reduce platelet aggregation?")
    print(json.dumps(result, indent=2))


