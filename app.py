import streamlit as st
import pandas as pd
from backend.data_loader import load_data, auto_clean
from backend.auto_profiler import get_basic_stats
from backend.qwen_client import query_qwen
from utils.safe_executor import execute_code

# Page config
st.set_page_config(
    page_title="AutoInsight – AI Data Analyst",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.stChatMessage { padding: 1rem; }
.stButton>button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Upload
with st.sidebar:
    st.image("https://via.placeholder.com/150x40?text=AutoInsight", use_container_width=True)
    st.subheader("📤 Upload Data")
    uploaded_file = st.file_uploader("CSV or Excel", type=["csv", "xlsx", "xls"])
    
    if uploaded_file:
        try:
            df = load_data(uploaded_file)
            if df.empty or df.shape[1] == 0:
                st.error("❌ No valid data found. Check file structure.")
                st.session_state.df = None
            else:
                df = auto_clean(df)
                st.session_state.df = df
                st.session_state.messages = []
                st.success("✅ Data loaded & cleaned!")
        except Exception as e:
            st.error(f"❌ {e}")
            st.session_state.df = None

# Main layout
if st.session_state.df is not None and not st.session_state.df.empty:
    df = st.session_state.df
    
    # Top stats
    stats = get_basic_stats(df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Rows", stats["rows"])
    col2.metric("Columns", stats["columns"])
    col3.metric("Missing Cells", stats["missing_cells"])
    
    # Preview
    with st.expander("🔍 Data Preview (first 5 rows)"):
        st.dataframe(df.head(), use_container_width=True)
    
    # Chat interface
    st.divider()
    st.subheader("💬 Ask Your Data Anything")
    st.caption("💡 Examples: _'Show calls with duration > 40'_, _'List very negative feedback'_")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "plot" in msg:
                st.plotly_chart(msg["plot"], use_container_width=True)
            if "table" in msg:
                st.dataframe(msg["table"], use_container_width=True)
    
    # User input
    if prompt := st.chat_input("Type your question in plain English..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Build rich context for LLM: column name, type, sample
        columns_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            sample_vals = df[col].dropna().head(2).tolist()
            sample_repr = str(sample_vals)[:60]
            columns_info.append(f"- {col} ({dtype}): {sample_repr}")
        sample_context = "\n".join(columns_info)
        
        with st.spinner("🧠 Analyzing..."):
            response = query_qwen(prompt, df.columns.tolist(), sample_context)
        
        # Parse response
        explanation = response.get("explanation", "No explanation available.")
        code = response.get("code", "")
        output_type = response.get("type", "value")
        
        assistant_msg = {"role": "assistant", "content": explanation}
        
        # Execute if code exists
        if code and output_type in ["plot", "value"]:
            result, result_type = execute_code(code, df)
            if result_type == "plot":
                assistant_msg["plot"] = result
            elif result_type == "table":
                assistant_msg["table"] = result
            else:
                assistant_msg["content"] += f"\n\n**Result:** {result}"
        
        # Save and display
        st.session_state.messages.append(assistant_msg)
        with st.chat_message("assistant"):
            st.write(assistant_msg["content"])
            if "plot" in assistant_msg:
                st.plotly_chart(assistant_msg["plot"], use_container_width=True)
            if "table" in assistant_msg:
                st.dataframe(assistant_msg["table"], use_container_width=True)

else:
    st.title("🏆 AutoInsight")
    st.subheader("Ask your data anything — in plain English.")
    st.write("1. Upload a CSV or Excel file\n2. Get instant insights\n3. Chat with AI to explore deeper")
    st.image("https://via.placeholder.com/800x300?text=Upload+Data+to+Get+Started", use_container_width=True)