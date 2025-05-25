import re
import streamlit as st
import traceback
from openai import OpenAI
import matplotlib.pyplot as plt

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def ask_llm_and_run(question, df, date_col="date", key_cols=None, target_col=None):
    # Sample if large dataset
    if len(df) > 1000:
        df = df.sample(1000, random_state=1).sort_index()

    csv_data = df.to_csv(index=False)
    key_cols_str = ", ".join(key_cols) if key_cols else "None"
    target_col_str = target_col if target_col else "None"

    system_prompt = (
        f"You are a Python data analysis assistant.\n"
        f"The dataset is in a DataFrame called 'df'.\n"
        f"The date/time column is: '{date_col}'\n"
        f"The key columns are: {key_cols_str}\n"
        f"The target column is: {target_col_str}\n\n"
        f"Instructions:\n"
        f"- Use the '{date_col}' column for weekly, monthly, or yearly trends.\n"
        f"- Use 'groupby' and aggregation for totals, max, min, averages.\n"
        f"- Use 'matplotlib.pyplot' for visualizations and assign the figure to 'result_fig'.\n"
        f"- For text/numeric answers, assign to variable 'result'.\n"
        f"- Do NOT include explanations. Just return executable Python code."
    )

    user_prompt = f"Dataset CSV:\n{csv_data}\n\nQuestion: {question}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
        )

        raw_code = response.choices[0].message.content.strip()

        # Clean up markdown formatting if any
        if raw_code.startswith("```"):
            code = re.sub(r"^```(?:python)?\n?|```$", "", raw_code, flags=re.MULTILINE).strip()
        else:
            code = raw_code.strip()

        local_env = {"df": df.copy(), "plt": plt}
        exec(code, {}, local_env)

        # Show result
        result = local_env.get("result", None)
        result_fig = local_env.get("result_fig", None)

        return code, result, result_fig

    except Exception as e:
        error_msg = f"Error running generated code:\n{traceback.format_exc()}"
        return "[Error] Code was not generated or failed.", error_msg, None
