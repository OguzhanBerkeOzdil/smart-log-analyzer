"""Streamlit UI for Smart Log Analyzer."""

import asyncio
import sys
from pathlib import Path

# Add src to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st

from smart_log_analyzer.core.engine import AnalysisEngine
from smart_log_analyzer.core.llm_providers import LLMProvider, get_provider
from smart_log_analyzer.core.models import ErrorGroup
from smart_log_analyzer.utils.generator import LogGenerator

# Page config
st.set_page_config(
    page_title="Smart Log Analyzer",
    page_icon="🔍",
    layout="wide",
)

# Custom CSS for better styling
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .error-card {
        background: #fff5f5;
        border-left: 4px solid #e53e3e;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .perf-card {
        background: #fffaf0;
        border-left: 4px solid #dd6b20;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .ai-card {
        background: #f0fff4;
        border-left: 4px solid #38a169;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
    }
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
</style>
""",
    unsafe_allow_html=True,
)


def main() -> None:
    # Header
    st.markdown(
        '<p class="main-header">🔍 Smart Log Analyzer</p>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="sub-header">Analyze server logs, detect error patterns, and get AI-powered insights</p>',
        unsafe_allow_html=True,
    )

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # AI Provider Selection
        st.subheader("🤖 AI Provider")
        ai_options = {
            "No AI": LLMProvider.NONE,
            "🌐 Google Gemini": LLMProvider.GEMINI,
            "🏠 Qwen 2.5 7B (Local)": LLMProvider.QWEN,
            "🏠 Phi-3.5 Mini (Local)": LLMProvider.PHI,
            "🏠 Llama 3.2 3B (Local)": LLMProvider.LLAMA,
        }
        selected_ai = st.selectbox(
            "Select AI for insights:",
            options=list(ai_options.keys()),
            index=0,
            help="Choose an AI provider for error analysis. Local models require Ollama.",
        )
        provider_type = ai_options[selected_ai]

        st.divider()

        # Log Source
        st.subheader("📁 Log Source")
        source_option = st.radio(
            "Choose log source:",
            ["Upload File", "Generate Synthetic", "Use Sample"],
            index=2,
        )

        log_path: Path | None = None

        if source_option == "Upload File":
            uploaded = st.file_uploader("Upload JSONL file", type=["jsonl", "json"])
            if uploaded:
                import time

                # Create unique temp file for each upload
                temp_dir = Path("data")
                temp_dir.mkdir(exist_ok=True)
                temp_path = temp_dir / f"uploaded_{int(time.time())}.jsonl"
                temp_path.write_bytes(uploaded.getvalue())
                log_path = temp_path
                st.success(f"✅ Uploaded {len(uploaded.getvalue())} bytes")

        elif source_option == "Generate Synthetic":
            count = st.slider("Number of logs", 50, 2000, 500, step=50)
            if st.button("🎲 Generate"):
                import time

                gen_path = Path(f"data/synthetic_{int(time.time())}.jsonl")
                LogGenerator(gen_path, count=count).generate()
                log_path = gen_path
                st.success(f"✅ Generated {count} logs!")

        else:  # Use Sample
            sample_path = Path("data/sample_logs.jsonl")
            if sample_path.exists():
                log_path = sample_path
            else:
                st.warning("Sample file not found. Generate logs first.")

        st.divider()

        # Info box
        if provider_type != LLMProvider.NONE:
            if provider_type == LLMProvider.GEMINI:
                st.info("🌐 Using Gemini API (requires GEMINI_API_KEY)")
            else:
                st.info(f"🏠 Using local model via Ollama: {provider_type.value}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        analyze_btn = st.button(
            "🚀 Analyze Logs", type="primary", use_container_width=True
        )

    with col2:
        if log_path:
            st.success(f"📄 {log_path.name}")
        else:
            st.warning("No log file selected")

    # Run analysis
    if analyze_btn and log_path:
        # Clear previous results from cache
        st.cache_data.clear()

        # Show analysis mode
        ai_badge = (
            f"🌐 {selected_ai}"
            if provider_type != LLMProvider.NONE
            else "📊 Manual Analysis"
        )
        st.info(f"**Analysis Mode:** {ai_badge}")

        with st.spinner("🔍 Analyzing logs..."):
            # Run analysis WITHOUT built-in AI (we'll use custom provider)
            results = asyncio.run(AnalysisEngine(enable_ai=False).run(log_path))

        # Display results
        st.markdown("---")
        st.header("📊 Analysis Results")

        # Metrics row
        error_result = results.get("Error Analysis")
        perf_result = results.get("Performance Analysis")

        if error_result and error_result["kind"] == "error":
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔴 Total Errors", error_result["total_errors"])
            with col2:
                st.metric("🔶 Unique Errors", error_result["unique_errors"])

            if perf_result and perf_result["kind"] == "performance":
                with col3:
                    st.metric(
                        "⏱️ Avg Duration", f"{perf_result['average_duration_ms']} ms"
                    )
                with col4:
                    st.metric(
                        "📊 Requests Analyzed",
                        perf_result["total_requests_with_duration"],
                    )

        # Detailed results in tabs
        tab1, tab2, tab3 = st.tabs(["🔴 Errors", "⏱️ Performance", "🤖 AI Insights"])

        with tab1:
            if error_result and error_result["kind"] == "error":
                st.subheader("Top Recurring Errors")
                for i, group in enumerate(error_result["top_errors"][:10], 1):
                    with st.container():
                        st.markdown(
                            f"""
                        <div class="error-card">
                            <strong>#{i}</strong> &nbsp;
                            <span style="background:#e53e3e;color:white;padding:2px 8px;border-radius:4px;">
                                {group.count}x
                            </span>
                            &nbsp; <strong>{group.service}</strong><br>
                            <code>{group.message}</code>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

        with tab2:
            if perf_result and perf_result["kind"] == "performance":
                st.subheader("Slowest Requests")
                for i, req in enumerate(perf_result["slowest_requests"][:10], 1):
                    duration_color = (
                        "#e53e3e" if (req.duration_ms or 0) > 1000 else "#dd6b20"
                    )
                    st.markdown(
                        f"""
                    <div class="perf-card">
                        <strong>#{i}</strong> &nbsp;
                        <span style="background:{duration_color};color:white;padding:2px 8px;border-radius:4px;">
                            {req.duration_ms} ms
                        </span>
                        &nbsp; <strong>{req.service}</strong>
                        &nbsp; <code>{req.request_id}</code>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

        with tab3:
            if provider_type == LLMProvider.NONE:
                st.info(
                    "🤖 Select an AI provider from the sidebar to get insights on errors."
                )
            elif (
                error_result
                and error_result["kind"] == "error"
                and error_result["top_errors"]
            ):
                top_error: ErrorGroup = error_result["top_errors"][0]
                st.subheader(f"AI Analysis: {top_error.message[:50]}...")

                with st.spinner(f"Getting insights from {selected_ai}..."):
                    provider = get_provider(provider_type)
                    if provider:
                        insight = provider.get_insight(top_error)
                        st.markdown(
                            f"""
                        <div class="ai-card">
                            <strong>🤖 {provider.name}</strong><br><br>
                            {insight}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No errors found to analyze.")

    elif analyze_btn and not log_path:
        st.error("Please select or generate a log file first!")

    # Footer
    st.markdown("---")
    st.markdown(
        """
    <div style="text-align:center;color:#888;font-size:0.9rem;">
        Smart Log Analyzer • Built with Python & Streamlit • Advanced Python Programming Course
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
