import streamlit as st
import pandas as pd
from openai import OpenAI

class SimpleDataCleaningAgent:
    def __init__(self, client, model="gpt-4.1-nano-2025-04-14"):
        self.client = client
        self.model = model
        self.generated_code = None
        self.cleaned_data = None

    def summarize_data(self, df):
        missing_counts = df.isnull().sum().to_dict()
        missing_str = ", ".join(f"{col}: {count}" for col, count in missing_counts.items())
        cols = list(df.columns)
        return f"Columns: {cols}; Missing values per column: {missing_str}"

    def generate_cleaning_code(self, df, instructions=""):
        summary = self.summarize_data(df)
        prompt = f"""
You are a helpful data cleaning assistant.
Dataset summary: {summary}
Instructions: {instructions}

Write a python function named `data_cleaner` that accepts a pandas DataFrame `df` and returns a cleaned DataFrame.
Cleaning steps should include:
- Drop columns with more than 40% missing values
- Impute numeric columns missing values with mean
- Impute categorical columns missing values with mode
- Remove duplicate rows
- Remove outliers beyond 3 * IQR (only if instructions don't forbid it)

Only provide the full python function code, nothing else.
"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        self.generated_code = response.choices[0].message.content
        return self.generated_code

    def run_cleaning(self, df):
        if self.generated_code is None:
            raise RuntimeError("No cleaning code generated yet.")

        # Clean generated code: remove markdown triple backticks if present
        code = self.generated_code.strip()
        if code.startswith("```") and code.endswith("```"):
            code = "\n".join(code.split("\n")[1:-1])  # remove first and last line

        local_vars = {}
        exec(code, {}, local_vars)
        cleaner_func = local_vars.get("data_cleaner")
        if cleaner_func:
            self.cleaned_data = cleaner_func(df)
            return self.cleaned_data
        else:
            raise RuntimeError("Cleaning function 'data_cleaner' not found in generated code.")

# Streamlit UI
st.title("🧹 AI Data Cleaning Agent")

st.write("""
Upload your CSV data, and the AI will generate a Python cleaning function based on your dataset summary.
Then it will apply that function to clean your data and display the results.
""")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Original Data Sample")
    st.dataframe(df.head())

    st.write("### Missing Values per Column")
    st.write(df.isnull().sum())

    instructions = st.text_area("Any special cleaning instructions? (e.g. 'Do not remove outliers.')", "")

    if st.button("Generate Cleaning Function and Clean Data"):
        try:
            client = OpenAI(api_key=st.secrets["openai"]["api_key"])
            agent = SimpleDataCleaningAgent(client=client)

            with st.spinner("Generating cleaning function code..."):
                code = agent.generate_cleaning_code(df, instructions=instructions)

            st.subheader("Generated Cleaning Function Code")
            st.code(code, language="python")

            with st.spinner("Running cleaning function on your data..."):
                cleaned_df = agent.run_cleaning(df)

            st.subheader("Cleaned Data Sample")
            st.dataframe(cleaned_df.head())

            st.success("Data cleaning complete!")

        except Exception as e:
            st.error(f"Error: {e}")

else:
    st.info("Please upload a CSV file to start.")
