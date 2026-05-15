"""
GraphRAG Benchmark Dashboard — Premium Streamlit UI
TigerGraph GraphRAG Inference Hackathon | PubMed Biomedical QA
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import concurrent.futures
import json
import os
import time
import pandas as pd
from datetime import datetime
from config import BENCHMARK_PATH

st.set_page_config(
    layout="wide",
    page_title="GraphRAG Benchmark | PubMed Biomedical QA",
    page_icon="🧬",
    initial_sidebar_state="expanded",
)

# ─── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark gradient background */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    color: #e2e8f0;
}

/* Glassmorphism cards */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 20px;
    margin: 8px 0;
}

.pipeline-header {
    font-size: 1.1em;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 10px 18px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 14px;
}

.answer-box {
    background: rgba(255,255,255,0.04);
    border-left: 3px solid rgba(255,255,255,0.2);
    padding: 14px;
    border-radius: 0 10px 10px 0;
    font-size: 0.88em;
    line-height: 1.7;
    height: 260px;
    overflow-y: auto;
    color: #cbd5e1;
}

.winner-badge {
    display: inline-block;
    background: linear-gradient(135deg, #00b894, #00cec9);
    color: white;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 700;
    margin-left: 8px;
    vertical-align: middle;
}

.reduction-banner {
    background: linear-gradient(135deg, rgba(0,184,148,0.15), rgba(0,206,201,0.15));
    border: 1px solid rgba(0,184,148,0.4);
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    margin: 18px 0;
}

.reduction-banner h2 {
    margin: 0;
    font-size: 1.8em;
    font-weight: 700;
    background: linear-gradient(135deg, #00b894, #00cec9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.reduction-banner p {
    margin: 6px 0 0;
    color: #94a3b8;
    font-size: 0.95em;
}

.hero-stat {
    text-align: center;
    padding: 16px;
}
.hero-stat .value {
    font-size: 2.4em;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-stat .label {
    font-size: 0.8em;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

/* Metric overrides */
[data-testid="stMetricValue"] { color: #e2e8f0 !important; }
[data-testid="stMetricLabel"] { color: #94a3b8 !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    color: #94a3b8;
}
.stTabs [aria-selected="true"] {
    background: rgba(102,126,234,0.2) !important;
    color: #667eea !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 25px rgba(102,126,234,0.4);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15,15,26,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 10px; }
</style>
""",
    unsafe_allow_html=True,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────

PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter"),
    margin=dict(t=30, b=10, l=10, r=10),
)

P1_COLOR = "#ef4444"
P2_COLOR = "#f59e0b"
P3_COLOR = "#10b981"


def _safe_avg(results_list, pipe_key, metric_key):
    vals = [
        r.get("results", {}).get(pipe_key, {}).get(metric_key, 0)
        for r in results_list
    ]
    non_zero = [v for v in vals if v]
    return sum(non_zero) / len(non_zero) if non_zero else 0


def _load_benchmark():
    if os.path.exists(BENCHMARK_PATH):
        with open(BENCHMARK_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def _load_eval():
    if os.path.exists("results/eval_summary.json"):
        with open("results/eval_summary.json", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "# 🧬 GraphRAG\n### vs RAG vs LLM"
    )
    st.markdown(
        """
<div style='color:#64748b;font-size:0.82em;margin:-8px 0 16px'>
TigerGraph Inference Hackathon
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("**Dataset**")
    st.markdown(
        "PubMed QA · pqa_labeled + pqa_unlabeled  \n2 M+ tokens of biomedical research"
    )

    st.markdown("---")
    st.markdown("**Pipelines**")
    st.markdown(
        "🔴 **LLM Only** — Raw Gemini  \n🟡 **Basic RAG** — ChromaDB  \n🟢 **GraphRAG** — TigerGraph"
    )

    st.markdown("---")
    st.markdown("**Winning Metric**")
    st.markdown(
        "_GraphRAG tokens < RAG tokens_  \n_with ≥ 90% answer accuracy_"
    )

    hist = _load_benchmark()
    if hist:
        st.markdown("---")
        st.markdown(f"**{len(hist)} queries benchmarked**")

    ev = _load_eval()
    if ev:
        p3 = ev.get("pipeline3", {})
        pr = p3.get("llm_judge_pass_rate", 0)
        bs = p3.get("avg_bertscore_f1", 0)
        st.markdown(
            f"GraphRAG judge pass rate: **{pr*100:.0f}%**  \n"
            f"GraphRAG BERTScore F1: **{bs:.3f}**"
        )

# ─── Title ────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center;background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);"
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    "font-size:2.6em;font-weight:800;margin-bottom:4px'>"
    "🧬 GraphRAG · RAG · LLM Benchmark"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center;color:#64748b;font-size:0.95em;margin-bottom:28px'>"
    "TigerGraph GraphRAG Inference Hackathon | PubMed Biomedical QA</p>",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs(["🚀 Live Demo", "📊 Benchmark Results", "💰 ROI Calculator"])

# ─── TAB 1: LIVE DEMO ─────────────────────────────────────────────────────────
with tab1:
    SAMPLE_QUESTIONS = [
        "Does aspirin reduce platelet aggregation in patients with cardiovascular disease?",
        "What are the side effects of metformin in elderly patients with type 2 diabetes?",
        "Is there a link between vitamin D deficiency and depression?",
        "What treatments are most effective for antibiotic-resistant tuberculosis?",
        "Does regular exercise reduce the risk of Alzheimer's disease?",
        "What is the relationship between gut microbiome and mental health?",
    ]

    col_q, col_s = st.columns([3, 2])

    with col_q:
        query = st.text_area(
            "Your biomedical question:",
            placeholder="e.g., Does aspirin reduce platelet aggregation?",
            height=110,
            key="main_query",
        )

    with col_s:
        st.markdown(
            "<span style='color:#64748b;font-size:0.85em'>Sample questions:</span>",
            unsafe_allow_html=True,
        )
        for idx, sq in enumerate(SAMPLE_QUESTIONS[:4]):
            if st.button(f"→ {sq[:52]}…", key=f"sample_{idx}", use_container_width=True):
                st.session_state["_selected"] = sq

    if "_selected" in st.session_state:
        query = st.session_state.pop("_selected")
        st.rerun()

    run_btn = st.button(
        "⚡ Run All 3 Pipelines Simultaneously",
        type="primary",
        use_container_width=True,
        key="run_btn",
    )

    if run_btn and query:
        from pipeline1_llm import run_pipeline1
        from pipeline2_rag import run_pipeline2
        from pipeline3_graphrag import run_pipeline3

        with st.spinner("Running all 3 pipelines in parallel…"):
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                f1 = executor.submit(run_pipeline1, query)
                f2 = executor.submit(run_pipeline2, query)
                f3 = executor.submit(run_pipeline3, query)
                r1, r2, r3 = f1.result(), f2.result(), f3.result()

        st.success("✅ All pipelines completed!")

        # Token reduction banner
        if r2["total_tokens"] > 0 and r3["total_tokens"] > 0:
            reduction = (1 - r3["total_tokens"] / r2["total_tokens"]) * 100
            direction = "fewer" if reduction > 0 else "more"
            abs_r = abs(reduction)
            color = "#00b894" if reduction > 0 else "#ef4444"
            st.markdown(
                f"""<div class="reduction-banner">
<h2 style="color:{color}">🎯 GraphRAG used {abs_r:.1f}% {direction} tokens than Basic RAG</h2>
<p>Same question — smarter multi-hop context = lower cost at scale</p>
</div>""",
                unsafe_allow_html=True,
            )

        # Three-column answers
        c1, c2, c3 = st.columns(3)
        configs = [
            (c1, r1, "🔴 LLM Only", P1_COLOR),
            (c2, r2, "🟡 Basic RAG", P2_COLOR),
            (c3, r3, "🟢 GraphRAG", P3_COLOR),
        ]
        for col, res, label, color in configs:
            with col:
                st.markdown(
                    f'<div class="pipeline-header" style="background:{color}22;'
                    f'border:1px solid {color}55;color:{color}">{label}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="answer-box">{res["answer"]}</div>',
                    unsafe_allow_html=True,
                )
                m1, m2 = st.columns(2)
                m1.metric("Total Tokens", f"{res['total_tokens']:,}")
                m2.metric("Latency", f"{res['latency_seconds']:.1f}s")
                m3, m4 = st.columns(2)
                m3.metric("Cost USD", f"${res['cost_usd']:.5f}")
                m4.metric("Prompt Tok.", f"{res['prompt_tokens']:,}")

        # Stacked bar chart
        st.markdown("---")
        st.markdown("### 📊 Token Usage Breakdown")

        fig = go.Figure()
        cats = ["LLM Only", "Basic RAG", "GraphRAG"]
        prompt_vals = [r1["prompt_tokens"], r2["prompt_tokens"], r3["prompt_tokens"]]
        completion_vals = [
            r1["completion_tokens"],
            r2["completion_tokens"],
            r3["completion_tokens"],
        ]
        colors_light = ["rgba(239,68,68,0.33)", "rgba(245,158,11,0.33)", "rgba(16,185,129,0.33)"]
        colors_full = [P1_COLOR, P2_COLOR, P3_COLOR]

        fig.add_trace(
            go.Bar(
                name="Prompt Tokens",
                x=cats,
                y=prompt_vals,
                marker_color=colors_light,
                text=[f"{v:,}" for v in prompt_vals],
                textposition="inside",
                textfont=dict(color="white"),
            )
        )
        fig.add_trace(
            go.Bar(
                name="Completion Tokens",
                x=cats,
                y=completion_vals,
                marker_color=colors_full,
                text=[f"{v:,}" for v in completion_vals],
                textposition="inside",
                textfont=dict(color="white"),
            )
        )
        fig.update_layout(
            barmode="stack",
            height=360,
            yaxis_title="Token Count",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Optional accuracy check
        st.markdown("---")
        with st.expander("🎯 Optional: Paste gold answer to evaluate accuracy"):
            gold_ref = st.text_area("Reference answer:", height=80, key="gold_ref")
            if gold_ref and st.button("Evaluate Accuracy", key="eval_btn"):
                from evaluate import evaluate_answer

                with st.spinner("Evaluating with LLM-as-Judge + BERTScore…"):
                    e1 = evaluate_answer(r1["answer"], gold_ref, query)
                    e2 = evaluate_answer(r2["answer"], gold_ref, query)
                    e3 = evaluate_answer(r3["answer"], gold_ref, query)

                ea, eb, ec = st.columns(3)
                for col, ev_r, name in [
                    (ea, e1, "LLM Only"),
                    (eb, e2, "Basic RAG"),
                    (ec, e3, "GraphRAG"),
                ]:
                    with col:
                        color = "🟢" if ev_r["llm_judge"] == "PASS" else "🔴"
                        st.markdown(f"**{name}**")
                        st.markdown(f"Judge: {color} **{ev_r['llm_judge']}**")
                        st.metric("BERTScore F1", f"{ev_r['bertscore_f1']:.3f}")

        # Auto-save to benchmark.json
        entry = {
            "timestamp": datetime.now().isoformat(),
            "question": query,
            "results": {"pipeline1": r1, "pipeline2": r2, "pipeline3": r3},
        }
        os.makedirs("results", exist_ok=True)
        try:
            with open(BENCHMARK_PATH, encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
       # Replace if same question exists, otherwise append
        existing = [e for e in existing if e["question"] != query]
        existing.append(entry)
        with open(BENCHMARK_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2)

# ─── TAB 2: BENCHMARK RESULTS ─────────────────────────────────────────────────
with tab2:
    st.markdown("### 📊 Full Benchmark Results")

    all_results = _load_benchmark()

    if not all_results:
        st.info(
            "No benchmark data yet. Run the Live Demo above, or run:\n"
            "```bash\npython run_benchmark.py\n```"
        )
    else:
        p1_avg = _safe_avg(all_results, "pipeline1", "total_tokens")
        p2_avg = _safe_avg(all_results, "pipeline2", "total_tokens")
        p3_avg = _safe_avg(all_results, "pipeline3", "total_tokens")
        reduction = (1 - p3_avg / p2_avg) * 100 if p2_avg > 0 else 0

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Queries Benchmarked", len(all_results))
        s2.metric("Avg Basic RAG Tokens", f"{p2_avg:,.0f}")
        s3.metric("Avg GraphRAG Tokens", f"{p3_avg:,.0f}")
        s4.metric("Token Reduction", f"{reduction:.1f}%", delta=f"-{reduction:.1f}%")

        # Trend chart
        st.markdown("---")
        trend_fig = go.Figure()
        qs = [e["question"][:35] + "…" for e in all_results]
        for pipe, color, label in [
            ("pipeline1", P1_COLOR, "LLM Only"),
            ("pipeline2", P2_COLOR, "Basic RAG"),
            ("pipeline3", P3_COLOR, "GraphRAG"),
        ]:
            vals = [e.get("results", {}).get(pipe, {}).get("total_tokens", 0) for e in all_results]
            trend_fig.add_trace(
                go.Scatter(
                    x=list(range(1, len(vals) + 1)),
                    y=vals,
                    name=label,
                    line=dict(color=color, width=2),
                    mode="lines+markers",
                    marker=dict(size=6),
                )
            )
        trend_fig.update_layout(
            height=320,
            xaxis_title="Query #",
            yaxis_title="Total Tokens",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **PLOT_LAYOUT,
        )
        st.plotly_chart(trend_fig, use_container_width=True)

        # Data table
        rows = []
        for e in all_results:
            r = e.get("results", {})
            p2t = r.get("pipeline2", {}).get("total_tokens", 1) or 1
            p3t = r.get("pipeline3", {}).get("total_tokens", 0)
            rows.append(
                {
                    "Question": e["question"][:65] + "…",
                    "LLM Tokens": r.get("pipeline1", {}).get("total_tokens", 0),
                    "RAG Tokens": r.get("pipeline2", {}).get("total_tokens", 0),
                    "GraphRAG Tokens": p3t,
                    "Reduction": f"{(1 - p3t / p2t) * 100:.1f}%",
                    "LLM Cost ($)": f"${r.get('pipeline1', {}).get('cost_usd', 0):.5f}",
                    "RAG Cost ($)": f"${r.get('pipeline2', {}).get('cost_usd', 0):.5f}",
                    "GraphRAG Cost ($)": f"${r.get('pipeline3', {}).get('cost_usd', 0):.5f}",
                }
            )
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Eval summary
        ev_data = _load_eval()
        if ev_data:
            st.markdown("---")
            st.markdown("### 🎯 Accuracy Evaluation (LLM-Judge + BERTScore)")
            ea2, eb2, ec2 = st.columns(3)
            for col, key, label, color in [
                (ea2, "pipeline1", "🔴 LLM Only", P1_COLOR),
                (eb2, "pipeline2", "🟡 Basic RAG", P2_COLOR),
                (ec2, "pipeline3", "🟢 GraphRAG", P3_COLOR),
            ]:
                if key in ev_data:
                    d = ev_data[key]
                    with col:
                        st.markdown(
                            f'<div style="color:{color};font-weight:700;font-size:1.05em">{label}</div>',
                            unsafe_allow_html=True,
                        )
                        st.metric("Judge Pass Rate", f"{d['llm_judge_pass_rate']*100:.0f}%")
                        st.metric("BERTScore F1", f"{d['avg_bertscore_f1']:.3f}")
                        st.metric("Evaluated", f"{d['n_evaluated']} queries")
                        if d.get("meets_judge_bonus"):
                            st.success("✅ ≥90% accuracy bonus!")

        # Download button
        report_json = json.dumps({"benchmark": all_results, "evaluation": ev_data}, indent=2)
        st.download_button(
            "⬇️ Download Full Benchmark JSON",
            data=report_json,
            file_name="graphrag_benchmark_report.json",
            mime="application/json",
        )

# ─── TAB 3: ROI CALCULATOR ────────────────────────────────────────────────────
with tab3:
    st.markdown("### 💰 Business Case: Real-World Cost Savings with GraphRAG")
    st.markdown("*Quantify the financial impact for your organisation*")

    col_l, col_r = st.columns(2)

    with col_l:
        queries_per_day = st.slider("Queries per day", 100, 100_000, 10_000, 500)
        working_days = st.slider("Working days per year", 200, 365, 250)
        rag_tokens = st.number_input(
            "Avg Basic RAG tokens / query", value=2500, step=100, min_value=100
        )
        gr_reduction = st.slider("GraphRAG token reduction %", 10, 80, 40)

    gr_tokens = rag_tokens * (1 - gr_reduction / 100)
    annual_queries = queries_per_day * working_days
    rag_cost = annual_queries * rag_tokens * 0.075 / 1_000_000
    gr_cost = annual_queries * gr_tokens * 0.075 / 1_000_000
    savings = rag_cost - gr_cost

    with col_r:
        st.markdown("#### 📈 Annual Impact")
        s1, s2 = st.columns(2)
        s1.metric("Annual Queries", f"{annual_queries:,.0f}")
        s2.metric("Tokens Saved/Query", f"{rag_tokens - gr_tokens:,.0f}")
        s3, s4 = st.columns(2)
        s3.metric("Basic RAG Annual Cost", f"${rag_cost:,.2f}")
        s4.metric("GraphRAG Annual Cost", f"${gr_cost:,.2f}")
        st.metric(
            "💰 Annual Savings",
            f"${savings:,.2f}",
            delta=f"-{gr_reduction}% cost",
            delta_color="inverse",
        )

    fig2 = go.Figure(
        data=[
            go.Bar(
                name="Basic RAG",
                x=["Annual Cost"],
                y=[rag_cost],
                marker_color=P2_COLOR,
                text=[f"${rag_cost:,.0f}"],
                textposition="outside",
                textfont=dict(color=P2_COLOR),
            ),
            go.Bar(
                name="GraphRAG",
                x=["Annual Cost"],
                y=[gr_cost],
                marker_color=P3_COLOR,
                text=[f"${gr_cost:,.0f}"],
                textposition="outside",
                textfont=dict(color=P3_COLOR),
            ),
        ]
    )
    fig2.update_layout(
        barmode="group",
        height=340,
        yaxis_title="USD / Year",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **PLOT_LAYOUT,
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(
        f"<p style='color:#64748b;font-size:0.85em;text-align:center'>"
        f"At {queries_per_day:,} queries/day, GraphRAG saves "
        f"<strong style='color:{P3_COLOR}'>${savings:,.0f}/year</strong> "
        f"vs Basic RAG on Gemini 1.5 Flash pricing ($0.075 per 1M input tokens).</p>",
        unsafe_allow_html=True,
    )

    # Multi-hop win examples expander
    with st.expander("🏆 Where GraphRAG Wins: Multi-Hop Examples"):
        st.markdown(
            """
GraphRAG shines on questions that require **connecting multiple pieces of evidence** across documents — 
something a single vector-search retrieval step can't do.

| Question type | Basic RAG | GraphRAG |
|---|---|---|
| Drug → mechanism → disease | Retrieves one drug chunk | Traverses Drug → Pathway → Disease nodes |
| Gene → expression → outcome | Misses downstream effect | Follows entity relationships 2 hops |
| Treatment comparison | Returns top-k semantically similar docs | Aggregates community summaries |

Run `python run_benchmark.py` and check the results table above to see concrete examples from PubMed QA.
"""
        )
