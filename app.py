import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI

# Initialize OpenAI client (make sure your API key is in secrets.toml as openai.api_key)
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

st.title("🧠 Time Series Forecasting AI Agent")

# Upload CSV or Excel
st.header("Step 1: Upload CSV or Excel")
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)

    st.write("Uploaded Data Sample:")
    st.dataframe(df.head())

    # Select time column
    time_col = st.selectbox("Select the time column", df.columns)

    # Select key columns (categorical/grouping)
    key_cols = st.multiselect("Select key columns (e.g. category columns)", [col for col in df.columns if col != time_col])

    # Select target column
    target_col = st.selectbox("Select the target column", [col for col in df.columns if col not in key_cols + [time_col]])

    # Prepare dataframe
    df[time_col] = pd.to_datetime(df[time_col])
    df_agent = df[[time_col] + key_cols + [target_col]].copy()

    st.success("✅ Data configured and ready!")
    st.dataframe(df_agent.head())

    # Store in session state
    st.session_state.df_agent = df_agent
    st.session_state.time_col = time_col
    st.session_state.key_cols = key_cols
    st.session_state.target_col = target_col

    # LLM chat
    st.header("🤖 Ask AI about your time series data")
    user_prompt = st.text_input("Ask me (e.g., plot trend, show seasonality, decompose)")

    if user_prompt:
        # Compose system message with context info
        system_msg = f"""
You are a time series data analyst. Given a DataFrame named df_agent with a time column '{time_col}', 
key columns {key_cols}, and target column '{target_col}', generate Python code that fulfills the user's request.
Return only Python code. Assume pandas, matplotlib.pyplot are already imported.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano-2025-04-14",  # or your preferred model
                #model="gpt-4o-mini",  # or your preferred model
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt}
                ],
            )
            generated_code = response.choices[0].message.content
            st.code(generated_code, language="python")
            
            # Clean generated_code from markdown backticks
            if generated_code.startswith("```"):
                generated_code = "\n".join(generated_code.split("\n")[1:])
            if generated_code.endswith("```"):
                generated_code = "\n".join(generated_code.split("\n")[:-1])
            
            # Run the generated code safely
            local_vars = {
                "df_agent": df_agent,
                "pd": pd,
                "plt": plt,
            }
            exec(generated_code, {}, local_vars)
            st.pyplot(plt)
            plt.clf()

        except Exception as e:
            st.error(f"Error running generated code: {e}")
