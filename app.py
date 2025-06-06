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
        You are a time series data analyst. You are working with a DataFrame named `df_agent`, which contains:
        - A time column: '{time_col}'
        - Key columns: {key_cols}
        - A target column: '{target_col}'

        Your tasks:
        1. Always group the data by the time column and key columns, aggregating the target column using `.sum()`.
        2. If the user asks for trends (e.g., 'plot trend for USA'), plot the time series of the target column after applying any filters.
        3. If the user asks for a maximum/minimum/average (e.g., 'max sales in USA'), return only the numeric value using `.max()`, `.min()`, or `.mean()` accordingly.
        4. Use `st.write()` to show numeric results, and `plt` for visualizations with `st.pyplot()`.
        5. Apply filters (like 'USA' or 'Product A') after aggregation based on the appropriate key columns.
        6. Do not include natural language explanations — return only Python code.

        Assume `pandas as pd`, `matplotlib.pyplot as plt`, and `streamlit as st` are already imported.
    """


        try:
            response = client.chat.completions.create(
                model="gpt-4.1-nano-2025-04-14",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_prompt}
                ],
            )
            generated_response = response.choices[0].message.content

            # Extract python code from response
            if "```python" in generated_response:
                code_block = generated_response.split("```python")[1]
                code = code_block.split("```")[0].strip()
            elif "```" in generated_response:
                code = generated_response.split("```")[1].strip()
            else:
                code = generated_response.strip()

            st.code(code, language="python")

            # If code contains matplotlib plot commands but no st.pyplot call, add it with explicit figure
            if "plt" in code and "st.pyplot" not in code:
                code += "\nst.pyplot(plt.gcf())\nplt.clf()"

            # Execute the generated code - pass local_vars as globals for exec
            local_vars = {
                "df_agent": df_agent,
                "pd": pd,
                "plt": plt,
                "st": st
            }
            exec(code, local_vars)

        except Exception as e:
            st.error(f"Error running generated code: {e}")



