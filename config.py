import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GRAPHRAG_BASE_URL = os.getenv("GRAPHRAG_BASE_URL", "http://localhost:8000")
GRAPHRAG_USERNAME = os.getenv("GRAPHRAG_USERNAME", "tigergraph")
GRAPHRAG_PASSWORD = os.getenv("GRAPHRAG_PASSWORD", "tigergraph")
GRAPHRAG_GRAPH_NAME = os.getenv("GRAPHRAG_GRAPH_NAME", "TigerGraphRAG")
MODEL = os.getenv("GEMINI_MODEL", "gemma-4-31b-it")

# Gemini 1.5 Flash pricing (per token, USD)
PRICE_INPUT = 0.075 / 1_000_000
PRICE_OUTPUT = 0.30 / 1_000_000

# Legacy aliases used in older code
GEMINI_FLASH_PRICE_INPUT = PRICE_INPUT
GEMINI_FLASH_PRICE_OUTPUT = PRICE_OUTPUT

# Paths
DATA_DIR = "data"
CHUNKS_PATH = "data/chunks/chunks.json"
QA_PAIRS_PATH = "data/qa_pairs.json"
BENCHMARK_PATH = "results/benchmark_final.json"
EVAL_SUMMARY_PATH = "results/eval_summary.json"
CHROMA_PATH = "./chroma_db"