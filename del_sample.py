# app.py
import streamlit as st
import pandas as pd
from utils.llm_agent import ask_llm_and_run

st.set_page_config(page_title="🧠 LLM Time Series Assistant")

st.title("🧠 Ask Your Data Anything")

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

        # Forward/backward fill
        df_processed = df_processed.sort_values(by=[*key_cols, date_col])
        df_processed = df_processed.groupby(key_cols, group_keys=False).apply(lambda g: g.ffill().bfill()).reset_index(drop=True)

        # Store processed dataframe in session
        st.session_state.df_processed = df_processed

        with st.sidebar:
            csv = df_processed.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Processed Data", data=csv, file_name="processed_data.csv")

        st.subheader("📊 Processed Data")
        # Optional: st.dataframe(df_processed.head())

        # Ask a question about processed data
        question = st.text_input("Ask question about processed data- note that processed data only has key cols:", key="ask_processed")

        if question:
            st.write(f"🔍 You asked: *{question}*")
            with st.spinner("Thinking..."):
                try:
                    #code, result = ask_llm_and_run(question, df_processed, date_col=date_col)
                    code, result = ask_llm_and_run(question, st.session_state.df_processed, 
                                                   date_col=date_col, key_cols=key_cols, target_col=target_col)

                    st.subheader("🧾 Generated Python Code")
                    st.code(code, language="python")

                    st.subheader("📊 Output")
                    st.write(result)

                except Exception as e:
                    st.error(f"⚠️ Something went wrong: {e}")
