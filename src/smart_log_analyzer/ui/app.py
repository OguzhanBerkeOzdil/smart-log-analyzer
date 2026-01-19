"""Streamlit UI for Smart Log Analyzer with Multi-LLM Support."""

import asyncio
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from smart_log_analyzer.core.engine import AnalysisEngine
from smart_log_analyzer.core.llm_providers import LLMProvider, get_provider
from smart_log_analyzer.core.models import ErrorGroup
from smart_log_analyzer.utils.generator import LogGenerator

st.set_page_config(page_title="Smart Log Analyzer", page_icon="🔍", layout="wide")

# Session state
if "log_path" not in st.session_state:
    st.session_state.log_path = None
if "results" not in st.session_state:
    st.session_state.results = None
if "ai_insights" not in st.session_state:
    st.session_state.ai_insights = None
if "provider_name" not in st.session_state:
    st.session_state.provider_name = None
if "ai_processing_time" not in st.session_state:
    st.session_state.ai_processing_time = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

# CSS
st.markdown(
    """
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; }
    .error-card { background: #fff5f5; border-left: 4px solid #e53e3e; padding: 1rem; margin: 0.5rem 0; border-radius: 0 8px 8px 0; }
    .ai-card { background: #f0fff4; border-left: 4px solid #38a169; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
    .no-ai-card { background: #f7fafc; border-left: 4px solid #a0aec0; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
</style>
""",
    unsafe_allow_html=True,
)


def run_analysis(log_path: Path) -> dict[str, Any]:
    """Run analysis without AI (AI is handled separately by selected LLM)."""
    return asyncio.run(AnalysisEngine(enable_ai=False).run(log_path))


def get_ai_insights_for_errors(
    errors: list[ErrorGroup], provider_type: LLMProvider
) -> tuple[list[dict[str, Any]], float]:
    """Get AI insights for multiple errors using selected LLM.

    Returns:
        Tuple of (insights list, processing time in seconds)
    """
    if provider_type == LLMProvider.NONE:
        return [], 0.0

    provider = get_provider(provider_type)
    if not provider:
        return [], 0.0

    start_time = time.time()
    insights: list[dict[str, Any]] = []
    for error in errors[:5]:  # Top 5 errors
        insight = provider.get_insight(error)
        insights.append(
            {
                "error": error,
                "insight": insight,
                "provider": provider.name,
            }
        )
    processing_time = time.time() - start_time
    return insights, processing_time


def main() -> None:
    st.markdown(
        '<p class="main-header">🔍 Smart Log Analyzer</p>', unsafe_allow_html=True
    )
    st.markdown("Analyze logs with **AI-powered insights** using local LLMs")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Selection - LOCAL LLMs ONLY
        st.subheader("🤖 AI Model")
        ai_options = {
            "❌ No AI (Manual Only)": LLMProvider.NONE,
            "🏠 Qwen 2.5 7B": LLMProvider.QWEN,
            "🏠 Phi-3.5 Mini": LLMProvider.PHI,
            "🏠 Llama 3.2 3B": LLMProvider.LLAMA,
        }
        selected_ai = st.selectbox("Select Model:", list(ai_options.keys()), index=0)
        provider_type = ai_options[selected_ai]

        if provider_type != LLMProvider.NONE:
            st.success(f"✅ AI Mode: {selected_ai}")
        else:
            st.warning("⚠️ Manual Mode - No AI analysis")

        st.divider()

        # Log Source
        st.subheader("📁 Log Source")
        source = st.radio("Source:", ["Generate", "Upload", "Sample"])

        if source == "Generate":
            count = st.slider("Log count:", 100, 2000, 500, 100)
            if st.button("🎲 Generate Logs", use_container_width=True):
                path = Path(f"data/gen_{int(time.time())}.jsonl")
                path.parent.mkdir(exist_ok=True)
                LogGenerator(path, count).generate()
                st.session_state.log_path = path
                st.session_state.results = None
                st.session_state.ai_insights = None
                st.rerun()

        elif source == "Upload":
            uploaded = st.file_uploader("Upload JSONL:", type=["jsonl"])
            if uploaded:
                # Only process if it's a new file
                if st.session_state.uploaded_file_name != uploaded.name:
                    path = Path(f"data/upload_{uploaded.name}")
                    path.parent.mkdir(exist_ok=True)
                    path.write_bytes(uploaded.getvalue())
                    st.session_state.log_path = path
                    st.session_state.uploaded_file_name = uploaded.name
                    st.session_state.results = None
                    st.session_state.ai_insights = None
                    st.rerun()

        else:  # Sample
            sample = Path("data/sample_logs.jsonl")
            if sample.exists() and st.button(
                "📄 Load Sample", use_container_width=True
            ):
                st.session_state.log_path = sample
                st.session_state.results = None
                st.session_state.ai_insights = None
                st.rerun()

        st.divider()
        if st.session_state.log_path:
            st.success(f"📄 {st.session_state.log_path.name}")

    # Main content
    col1, col2 = st.columns([3, 1])
    with col1:
        analyze_btn = st.button("🚀 ANALYZE", type="primary", use_container_width=True)
    with col2:
        mode = selected_ai if provider_type != LLMProvider.NONE else "📊 Manual"
        st.info(mode)

    if analyze_btn:
        if not st.session_state.log_path or not st.session_state.log_path.exists():
            st.error("❌ Load a log file first!")
        else:
            with st.spinner("🔍 Running analysis..."):
                # Step 1: Run base analysis
                st.session_state.results = run_analysis(st.session_state.log_path)

                # Step 2: Get AI insights if LLM selected
                error_result = st.session_state.results.get("Error Analysis")
                if error_result and error_result["top_errors"]:
                    if provider_type != LLMProvider.NONE:
                        with st.spinner(
                            f"🤖 Getting AI insights from {selected_ai}..."
                        ):
                            insights, proc_time = get_ai_insights_for_errors(
                                error_result["top_errors"], provider_type
                            )
                            st.session_state.ai_insights = insights
                            st.session_state.ai_processing_time = proc_time
                            st.session_state.provider_name = selected_ai
                    else:
                        st.session_state.ai_insights = None
                        st.session_state.ai_processing_time = None
                        st.session_state.provider_name = None

            st.rerun()

    # Display Results
    if st.session_state.results:
        st.markdown("---")

        error_result = st.session_state.results.get("Error Analysis")
        perf_result = st.session_state.results.get("Performance Analysis")

        # Metrics row
        if error_result:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("🔴 Total Errors", error_result["total_errors"])
            c2.metric("🔶 Unique Errors", error_result["unique_errors"])
            if perf_result:
                c3.metric(
                    "⏱️ Avg Log Duration", f"{perf_result['average_duration_ms']} ms"
                )
                c4.metric("📊 Requests", perf_result["total_requests_with_duration"])

            # Show AI processing time if available
            if st.session_state.ai_processing_time is not None:
                c5 = st.columns(1)[0]
                c5.metric(
                    "🤖 AI Processing",
                    f"{st.session_state.ai_processing_time:.2f}s",
                )

        # Results display based on mode
        if st.session_state.ai_insights:
            # AI MODE - Show errors WITH AI analysis
            st.header(f"🤖 AI Analysis Results ({st.session_state.provider_name})")
            st.markdown("Each error is analyzed by the selected AI model:")

            for i, item in enumerate(st.session_state.ai_insights, 1):
                error = item["error"]
                insight = item["insight"]

                st.markdown(f"### #{i} - {error.service}")
                col_err, col_ai = st.columns([1, 2])

                with col_err:
                    st.markdown(
                        f"""<div class="error-card">
                        <strong>Error ({error.count}x)</strong><br>
                        <code>{error.message}</code>
                    </div>""",
                        unsafe_allow_html=True,
                    )

                with col_ai:
                    st.markdown(
                        f"""<div class="ai-card">
                        <strong>🤖 AI Analysis:</strong><br>
                        {insight}
                    </div>""",
                        unsafe_allow_html=True,
                    )

                st.markdown("---")

        else:
            # MANUAL MODE - Show errors WITHOUT AI
            st.header("📊 Manual Analysis Results (No AI)")
            st.markdown(
                "Select an AI model from the sidebar to get intelligent insights!"
            )

            tab1, tab2 = st.tabs(["🔴 Errors", "⏱️ Performance"])

            with tab1:
                if error_result and error_result["top_errors"]:
                    for i, g in enumerate(error_result["top_errors"][:10], 1):
                        st.markdown(
                            f"""<div class="no-ai-card">
                            <strong>#{i}</strong>
                            <span style="background:#e53e3e;color:white;padding:2px 8px;border-radius:4px;margin:0 8px;">{g.count}x</span>
                            <strong>{g.service}</strong><br>
                            <code>{g.message}</code><br>
                            <em style="color:#999;">💡 Select an AI model to get analysis for this error</em>
                        </div>""",
                            unsafe_allow_html=True,
                        )

            with tab2:
                if perf_result and perf_result["slowest_requests"]:
                    for i, r in enumerate(perf_result["slowest_requests"][:10], 1):
                        color = "#e53e3e" if (r.duration_ms or 0) > 1000 else "#dd6b20"
                        st.markdown(
                            f"""<div class="no-ai-card">
                            <strong>#{i}</strong>
                            <span style="background:{color};color:white;padding:2px 8px;border-radius:4px;margin:0 8px;">{r.duration_ms} ms</span>
                            <strong>{r.service}</strong> <code>{r.request_id}</code>
                        </div>""",
                            unsafe_allow_html=True,
                        )

    st.markdown("---")
    st.caption("Smart Log Analyzer • Local LLM Support via Ollama")


if __name__ == "__main__":
    main()
