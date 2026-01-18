"""Streamlit UI for Smart Log Analyzer."""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from smart_log_analyzer.core.engine import AnalysisEngine
from smart_log_analyzer.core.llm_providers import LLMProvider, get_provider
from smart_log_analyzer.utils.generator import LogGenerator

# Page config
st.set_page_config(
    page_title="Smart Log Analyzer",
    page_icon="🔍",
    layout="wide",
)

# Initialize session state
if "log_path" not in st.session_state:
    st.session_state.log_path = None
if "results" not in st.session_state:
    st.session_state.results = None
if "ai_insight" not in st.session_state:
    st.session_state.ai_insight = None
if "selected_provider" not in st.session_state:
    st.session_state.selected_provider = None

# Custom CSS
st.markdown(
    """
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #666; margin-bottom: 2rem; }
    .error-card { background: #fff5f5; border-left: 4px solid #e53e3e; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0; }
    .perf-card { background: #fffaf0; border-left: 4px solid #dd6b20; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0; }
    .ai-card { background: #f0fff4; border-left: 4px solid #38a169; padding: 1rem; margin: 1rem 0; border-radius: 8px; }
    .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; font-weight: 600; }
</style>
""",
    unsafe_allow_html=True,
)


def run_analysis(log_path: Path) -> dict[str, Any]:
    """Run the analysis engine and return results."""
    return asyncio.run(AnalysisEngine(enable_ai=False).run(log_path))


def main() -> None:
    # Header
    st.markdown(
        '<p class="main-header">🔍 Smart Log Analyzer</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Analyze server logs, detect error patterns, and get AI-powered insights</p>',
        unsafe_allow_html=True,
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Provider Selection
        st.subheader("🤖 AI Provider")
        ai_options = {
            "No AI (Manual)": LLMProvider.NONE,
            "🌐 Google Gemini": LLMProvider.GEMINI,
            "🏠 Qwen 2.5 7B": LLMProvider.QWEN,
            "🏠 Phi-3.5 Mini": LLMProvider.PHI,
            "🏠 Llama 3.2 3B": LLMProvider.LLAMA,
        }
        selected_ai = st.selectbox(
            "Select AI:", options=list(ai_options.keys()), index=0
        )
        provider_type = ai_options[selected_ai]

        st.divider()

        # Log Source
        st.subheader("📁 Log Source")
        source_option = st.radio(
            "Source:", ["Generate New", "Upload File", "Use Sample"], index=0
        )

        if source_option == "Generate New":
            count = st.slider("Log count:", 100, 2000, 500, step=100)
            if st.button("🎲 Generate Logs", use_container_width=True):
                gen_path = Path(f"data/gen_{int(time.time())}.jsonl")
                gen_path.parent.mkdir(exist_ok=True)
                LogGenerator(gen_path, count=count).generate()
                st.session_state.log_path = gen_path
                st.session_state.results = None  # Clear old results
                st.session_state.ai_insight = None
                st.success(f"✅ Generated {count} logs!")
                st.rerun()

        elif source_option == "Upload File":
            uploaded = st.file_uploader("Upload JSONL:", type=["jsonl"])
            if uploaded:
                upload_path = Path(f"data/upload_{int(time.time())}.jsonl")
                upload_path.parent.mkdir(exist_ok=True)
                upload_path.write_bytes(uploaded.getvalue())
                st.session_state.log_path = upload_path
                st.session_state.results = None
                st.session_state.ai_insight = None
                st.success("✅ Uploaded!")

        else:  # Use Sample
            sample_path = Path("data/sample_logs.jsonl")
            if sample_path.exists():
                if st.button("📄 Load Sample", use_container_width=True):
                    st.session_state.log_path = sample_path
                    st.session_state.results = None
                    st.session_state.ai_insight = None
                    st.rerun()
            else:
                st.warning("No sample file. Generate first!")

        st.divider()

        # Show current file
        if st.session_state.log_path:
            st.success(f"📄 {st.session_state.log_path.name}")
        else:
            st.warning("No log file loaded")

    # Main content
    col1, col2 = st.columns([3, 1])

    with col1:
        if st.button("🚀 ANALYZE", type="primary", use_container_width=True):
            if st.session_state.log_path and st.session_state.log_path.exists():
                with st.spinner("🔍 Analyzing..."):
                    st.session_state.results = run_analysis(st.session_state.log_path)
                    st.session_state.selected_provider = provider_type

                    # Get AI insight if provider selected
                    if provider_type != LLMProvider.NONE:
                        error_result = st.session_state.results.get("Error Analysis")
                        if error_result and error_result["top_errors"]:
                            top_error = error_result["top_errors"][0]
                            provider = get_provider(provider_type)
                            if provider:
                                st.session_state.ai_insight = {
                                    "provider": provider.name,
                                    "error": top_error,
                                    "insight": provider.get_insight(top_error),
                                }
                    else:
                        st.session_state.ai_insight = None

                st.rerun()
            else:
                st.error("❌ Please load a log file first!")

    with col2:
        mode = "🤖 " + selected_ai if provider_type != LLMProvider.NONE else "📊 Manual"
        st.info(mode)

    # Display Results
    if st.session_state.results:
        st.markdown("---")
        st.header("📊 Analysis Results")

        error_result = st.session_state.results.get("Error Analysis")
        perf_result = st.session_state.results.get("Performance Analysis")

        # Metrics
        if error_result:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔴 Total Errors", error_result["total_errors"])
            c2.metric("🔶 Unique Errors", error_result["unique_errors"])
            if perf_result:
                c3.metric("⏱️ Avg Duration", f"{perf_result['average_duration_ms']} ms")
                c4.metric("📊 Requests", perf_result["total_requests_with_duration"])

        # Tabs
        tab1, tab2, tab3 = st.tabs(["🔴 Errors", "⏱️ Performance", "🤖 AI Insights"])

        with tab1:
            if error_result and error_result["top_errors"]:
                st.subheader("Top Recurring Errors")
                for i, g in enumerate(error_result["top_errors"][:10], 1):
                    st.markdown(
                        f"""<div class="error-card">
                        <strong>#{i}</strong>
                        <span style="background:#e53e3e;color:white;padding:2px 8px;border-radius:4px;margin:0 8px;">{g.count}x</span>
                        <strong>{g.service}</strong><br><code>{g.message}</code>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No errors found!")

        with tab2:
            if perf_result and perf_result["slowest_requests"]:
                st.subheader("Slowest Requests")
                for i, r in enumerate(perf_result["slowest_requests"][:10], 1):
                    color = "#e53e3e" if (r.duration_ms or 0) > 1000 else "#dd6b20"
                    st.markdown(
                        f"""<div class="perf-card">
                        <strong>#{i}</strong>
                        <span style="background:{color};color:white;padding:2px 8px;border-radius:4px;margin:0 8px;">{r.duration_ms} ms</span>
                        <strong>{r.service}</strong> <code>{r.request_id}</code>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No performance data!")

        with tab3:
            if st.session_state.ai_insight:
                ai = st.session_state.ai_insight
                st.subheader(f"🤖 {ai['provider']} Analysis")
                st.markdown(f"**Error:** `{ai['error'].message}`")
                st.markdown(
                    f"**Service:** {ai['error'].service} ({ai['error'].count}x)"
                )
                st.markdown("---")
                st.markdown(
                    f"""<div class="ai-card">{ai['insight']}</div>""",
                    unsafe_allow_html=True,
                )
            elif st.session_state.selected_provider == LLMProvider.NONE:
                st.info("💡 Select an AI provider from the sidebar to get insights!")
            else:
                st.warning("No AI insight available. Check if the model is running.")

    # Footer
    st.markdown("---")
    st.caption("Smart Log Analyzer • Advanced Python Programming")


if __name__ == "__main__":
    main()
