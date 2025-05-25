import streamlit as st
from utils.plots import plot_yearly_trend, plot_monthly_trend, plot_weekly_trend
from utils.llm_agent import ask_llm_and_run

def run_eda(df, time_col, target_col, key_cols):
    st.subheader("🧪 Exploratory Data Analysis")

    st.markdown("### 📅 Year-over-Year Trend")
    plot_yearly_trend(df, time_col, target_col)

    st.markdown("### 📆 Monthly Trend")
    plot_monthly_trend(df, time_col, target_col)

    st.markdown("### 📊 Weekly Trend")
    plot_weekly_trend(df, time_col, target_col)

    st.markdown("### 🤖 Ask the AI Agent")
    question = st.text_input("Ask a question (e.g. 'Which item has the highest sales?')")
    if question:
        response = ask_llm_and_run(question, df)[1]  # Only show result
        st.success(response)
