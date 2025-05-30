# app.py
import streamlit as st
import pandas as pd

from utils.llm_agent import ask_llm_and_run
from utils.plots import plot_yearly_trend, plot_monthly_trend, plot_weekly_trend
from utils.fill_missing_weeks import process_level

# Set layout
st.set_page_config(page_title="🧠 LLM Time Series Assistant", layout="wide")
st.title("🧠 Time Series Agent (WIP)")

# =========================
# 📂 SIDEBAR: Upload + Config
# =========================
with st.sidebar:
    st.header("📂 Upload Files")

    actual_file = st.file_uploader("📁 Upload Actuals File", type=["csv", "xlsx"])
    time_file = st.file_uploader("🕒 Upload Time Dimension File", type=["csv", "xlsx"])

    if actual_file and time_file:
        df_actual = pd.read_csv(actual_file) if actual_file.name.endswith(".csv") else pd.read_excel(actual_file)
        df_time = pd.read_csv(time_file) if time_file.name.endswith(".csv") else pd.read_excel(time_file)

        st.divider()
        st.header("🔧 Column Selection")

        date_col = st.selectbox("📅 Select Date Column", df_actual.columns)
        target_col = st.selectbox("🎯 Select Target Column", df_actual.columns)
        key_cols = st.multiselect("🔑 Select Forecast Level Columns", [col for col in df_actual.columns if col not in [date_col, target_col]])

        if date_col not in df_time.columns:
            st.error(f"❌ Date column '{date_col}' not found in time dimension file.")
        elif len(key_cols) == 0:
            st.warning("⚠️ Please select at least one key column.")
        else:
            # Parse datetime
            df_actual[date_col] = pd.to_datetime(df_actual[date_col])
            df_time[date_col] = pd.to_datetime(df_time[date_col])

            # Process data
            df_processed = process_level(df_actual, df_time[[date_col]], forecast_level=key_cols, col_sales=target_col)
            df_processed = df_processed[[date_col] + key_cols + [target_col]]

            # Store in session
            st.session_state.df_processed = df_processed
            st.session_state.date_col = date_col
            st.session_state.target_col = target_col
            st.session_state.key_cols = key_cols

            st.success("✅ Processing Complete")

# =========================
# 🧠 MAIN AREA
# =========================
if "df_processed" in st.session_state:
    df = st.session_state.df_processed
    date_col = st.session_state.date_col
    target_col = st.session_state.target_col
    key_cols = st.session_state.key_cols

    # 🔽 Mode Selector
    mode = st.selectbox("Choose Mode", ["🤖 LLM", "📊 EDA", "📈 Forecast"], index=0)

    # ⬇️ Download and Show Processed Data
    st.subheader("✅ Processed Data")
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Processed Data", data=csv, file_name="processed_actuals.csv", mime="text/csv")

    if st.button("👁 Show Processed Data Preview"):
        st.dataframe(df.head(), use_container_width=True)

    # -----------------------
    # 🤖 LLM Mode
    # -----------------------
    if mode == "🤖 LLM":
        st.markdown("### Ask the Time Series Agent")
        question = st.text_input("💬 Ask a question (e.g., trends, outliers, seasonality):")

        st.markdown("💡 Try questions like:")
        st.markdown("""
        - Which month had the highest sales?
        - What is the average sales by item?
        - Are there outliers in sales?
        - Show weekly trend of sales.
        """)

        if question:
            with st.spinner("Thinking..."):
                try:
                    code, result, result_fig = ask_llm_and_run(question, df, date_col, key_cols, target_col)

                    st.subheader("🧾 Generated Code")
                    st.code(code, language="python")

                    if result_fig is not None:
                        st.subheader("📊 Visualization")
                        st.pyplot(result_fig)

                    if result is not None:
                        st.subheader("📋 Output")
                        st.write(result)

                except Exception as e:
                    st.error(f"⚠️ Error: {e}")

    # -----------------------
    # 📊 EDA Mode
    # -----------------------
    elif mode == "📊 EDA":
        st.markdown("### Exploratory Data Analysis")

        st.subheader("📅 Year-over-Year Weekly Trend")
        plot_yearly_trend(df, date_col, target_col)

        st.subheader("📆 Monthly Aggregated Trend")
        plot_monthly_trend(df, date_col, target_col)

        st.subheader("🗓️ Weekly Aggregated Trend")
        plot_weekly_trend(df, date_col, target_col)

    # -----------------------
    # 📈 Forecast Mode (Coming Soon)
    # -----------------------
    elif mode == "📈 Forecast":
        st.markdown("### Forecast (Coming Soon 🚧)")
        st.info("This section is under development. You can add your forecast logic here.")

else:
    st.info("📥 Please upload both Actuals and Time files to begin.")
