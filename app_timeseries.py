# app.py
import streamlit as st
import pandas as pd
from utils.llm_agent import ask_llm_and_run
from utils.plots import plot_yearly_trend, plot_monthly_trend, plot_weekly_trend

st.set_page_config(page_title="🧠 LLM Time Series Assistant")
st.title("🧠 Time Series Agent(WIP)")

uploaded_file = st.file_uploader("📁 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load data
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head())

    with st.sidebar:
        st.markdown("### 🛠️ Configure Columns")
        date_col = st.selectbox("Select Date Column", df.select_dtypes(include='datetime').columns)
        target_col = st.selectbox("Select Target Column", df.select_dtypes(include='number').columns)
        key_cols = st.multiselect("Select Key Columns", df.columns.difference([date_col, target_col]))

    if date_col and target_col and key_cols:
        from utils.fill_missing_weeks import fill_missing_weeks

        # Fill missing weeks
        df_processed = fill_missing_weeks(df, date_col, target_col, key_cols)
        df_processed = df_processed.sort_values(by=[*key_cols, date_col])
        df_processed = df_processed.groupby(key_cols, group_keys=False).apply(lambda g: g.ffill().bfill()).reset_index(drop=True)
        st.session_state.df_processed = df_processed

        with st.sidebar:
            csv = df_processed.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Processed Data", data=csv, file_name="processed_data.csv")

        # ✅ NEW: Sidebar Mode Selector
        with st.sidebar:
            mode = st.selectbox("Choose Mode", ["LLM Q&A", "EDA", "Data Cleaning", "Time Series Forecasting"])

        # Show processed data
        st.subheader("📊 Processed Data")
        # st.dataframe(df_processed.head())  # Optional
        
        # Mode logic
        if mode == "EDA":
            st.subheader("📈 Year-over-Year Weekly Trend")
            plot_yearly_trend(df_processed, date_col, target_col)

            st.subheader("📆 Year-over-Year Monthly Trend")
            plot_monthly_trend(df_processed, date_col, target_col)

            st.subheader("🗓️ Weekly Trend (Aggregated)")
            plot_weekly_trend(df_processed, date_col, target_col)


        # If mode is "LLM Q&A", show the existing input box
        if mode == "LLM Q&A":
            question = st.text_input("Ask question about processed data- note that processed data only has key cols:", key="ask_processed")
            
                        
            st.markdown("💡 **Sample Questions to Ask:**")
            sample_qs = [
                "Which month had the highest sales?",
                "Show weekly sales trends over time.",
                "What is the average sales by item?",
                "What is the total sales by year?",
                "Which item had the most consistent sales?",
                "How many missing values are there in each column?",
                "Which key has the highest variance in sales?",
                "Are there any outliers in the sales column?"
            ]
            for q in sample_qs:
                st.markdown(f"- {q}")


            if question:
                st.write(f"🔍 You asked: *{question}*")
                with st.spinner("Thinking..."):
                    try:
                        code, result, result_fig = ask_llm_and_run(question, st.session_state.df_processed, 
                                                       date_col=date_col, key_cols=key_cols, target_col=target_col)

                        st.subheader("🧾 Generated Python Code")
                        st.code(code, language="python")
                        
                        if result_fig is not None:
                            st.pyplot(result_fig)
                        elif result is not None:
                            st.write(result)

                        st.subheader("📊 Output")
                        st.write(result)

                    except Exception as e:
                        st.error(f"⚠️ Something went wrong: {e}")

else:
    st.info("Please upload a CSV or Excel file to get started.")
