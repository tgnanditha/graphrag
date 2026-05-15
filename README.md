# 🧬 GraphRAG Inference — TigerGraph Hackathon

> **Biomedical Question Answering at Scale: Proving GraphRAG is smarter and cheaper than Basic RAG**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![TigerGraph](https://img.shields.io/badge/Graph_DB-TigerGraph_Cloud-orange?logo=data:image/svg+xml;base64,PHN2Zy8+)](https://tgcloud.io)
[![Gemini](https://img.shields.io/badge/LLM-Gemma%204-blueviolet?logo=google)](https://ai.google.dev)
[![Streamlit](https://img.shields.io/badge/Dashboard-Streamlit-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🏆 The Winning Metric

> **GraphRAG uses 72% fewer tokens than Basic RAG while maintaining comparable accuracy on 20 real biomedical questions from PubMed QA.**

| Pipeline | Avg Tokens | Avg Latency | Relative Cost |
|---|---|---|---|
| 🔴 LLM-Only | 204 | ~18s | Baseline |
| 🟡 Basic RAG | 589 | ~17s | 2.9× baseline |
| 🟢 **GraphRAG** | **165** | ~20s | **0.8× baseline** |

---

## 🧠 What It Does

This project compares **three AI pipelines** for answering biomedical yes/no questions from PubMed QA:

| Pipeline | Description |
|---|---|
| **Pipeline 1 — LLM Only** | Sends the question directly to the LLM with no external context |
| **Pipeline 2 — Basic RAG** | Retrieves top-5 text chunks from ChromaDB using vector similarity |
| **Pipeline 3 — GraphRAG** | Traverses a TigerGraph knowledge graph to retrieve structured, entity-linked context |

The key insight: GraphRAG fetches **targeted, structured facts** from the graph instead of pulling large raw chunks, achieving the same (or better) answer quality with far fewer tokens.

---

## 🗂️ Project Structure

```
graphrag-hackathon/
├── pipeline1_llm.py          # LLM-Only pipeline
├── pipeline2_rag.py          # Basic RAG pipeline (ChromaDB)
├── pipeline3_graphrag.py     # GraphRAG pipeline (TigerGraph)
├── run_benchmark.py          # Benchmarking engine — runs all 3 pipelines
├── evaluate.py               # LLM-judge + BERTScore evaluation
├── dashboard.py              # Streamlit visualization dashboard
├── config.py                 # Centralised config (model, paths, pricing)
├── build_index.py            # Builds ChromaDB vector index from chunks
├── download_data.py          # Downloads PubMed QA dataset
├── data/
│   ├── qa_pairs.json         # 20 curated yes/no questions with gold answers
│   └── chunks/chunks.json    # Text chunks for Basic RAG
├── results/
│   ├── benchmark_final.json  # Full benchmark results (all 3 pipelines × 20 Qs)
│   └── eval_summary.json     # LLM-judge pass rates + BERTScore F1 per pipeline
└── .env.template             # Template for environment variables
```

---

## ⚡ Quick Start

### 1. Clone & set up environment

```bash
git clone https://github.com/your-username/graphrag-hackathon.git
cd graphrag-hackathon

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.template .env
# Edit .env and fill in your credentials
```

```env
GEMINI_API_KEY=your_google_ai_studio_key
GRAPHRAG_BASE_URL=https://your-tigergraph-instance.tgcloud.io
GRAPHRAG_USERNAME=tigergraph
GRAPHRAG_PASSWORD=your_password
GRAPHRAG_GRAPH_NAME=TextChunksGraph
```

### 3. Download data & build index

```bash
python download_data.py    # Downloads PubMed QA dataset
python build_index.py      # Builds ChromaDB vector index
```

### 4. Run the benchmark

```bash
python run_benchmark.py    # ~10 min — runs all 3 pipelines on 20 questions
```

### 5. Evaluate results

```bash
python evaluate.py         # LLM judge + BERTScore scoring
```

### 6. View the dashboard

```bash
streamlit run dashboard.py
```

---

## 🔧 Tech Stack

| Component | Technology |
|---|---|
| **LLM** | Google Gemma 4 (`gemma-4-31b-it`) via Gemini API |
| **Graph Database** | TigerGraph Cloud (REST++ API) |
| **Vector Database** | ChromaDB (local) |
| **Embeddings** | `all-MiniLM-L6-v2` (sentence-transformers) |
| **Evaluation** | BERTScore F1 + Gemini LLM-as-Judge |
| **Dashboard** | Streamlit + Plotly |
| **Dataset** | [PubMed QA](https://pubmedqa.github.io/) (yes/no biomedical questions) |

---

## 📊 Key Results

The benchmark ran on **20 biomedical questions** from PubMed QA.

### Token Efficiency
- **GraphRAG saved 72% of tokens** compared to Basic RAG on average
- Per-question reduction ranged from **44.8% to 88.5%**

### Why GraphRAG wins on tokens
Basic RAG dumps raw text chunks (avg **589 tokens**) into the prompt. GraphRAG queries the TigerGraph knowledge graph for specific entities and relationships, building a **targeted, compact context** (avg **165 tokens**).

---

## 🔑 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google AI Studio API key | ✅ |
| `GRAPHRAG_BASE_URL` | TigerGraph Cloud instance URL | ✅ |
| `GRAPHRAG_USERNAME` | TigerGraph username (default: `tigergraph`) | ✅ |
| `GRAPHRAG_PASSWORD` | TigerGraph password | ✅ |
| `GRAPHRAG_GRAPH_NAME` | Graph name (default: `TextChunksGraph`) | ✅ |
| `GEMINI_MODEL` | Override LLM model (default: `gemma-4-31b-it`) | ❌ |

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for the TigerGraph GraphRAG Inference Hackathon 2025.*
