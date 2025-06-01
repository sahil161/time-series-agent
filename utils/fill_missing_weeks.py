import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import streamlit as st

# utils/fill_missing_weeks.py (rename to process_forecast_level.py or keep as is)

def process_level(df, df_time, forecast_level, col_sales):
    results = []
    total_combinations = df[forecast_level].drop_duplicates().shape[0]
    intersection_count = 0

    grouped = df.groupby(forecast_level)

    for keys, group in grouped:
        if not isinstance(keys, tuple):
            keys = (keys,)

        merged_group = pd.merge(df_time, group, on='Time.[Week]', how='left')

        for col, key in zip(forecast_level, keys):
            merged_group[col] = key

        merged_group.fillna(0, inplace=True)
        merged_group[col_sales] = merged_group[col_sales].clip(lower=0)

        merged_group.sort_values(by='Time.[Week]', inplace=True)
        merged_group['Cumulative Sum'] = merged_group[col_sales].cumsum()
        filtered_group = merged_group[merged_group['Cumulative Sum'] != 0].drop(columns=['Cumulative Sum'])

        results.append(filtered_group)
        intersection_count += 1
        print(f'Processed {intersection_count}/{total_combinations}')

    return pd.concat(results, ignore_index=True) if results else pd.DataFrame()




def plot_yearly_trend(df, time_col, y_col):
    df['Year'] = pd.to_datetime(df[time_col]).dt.year
    df['Week'] = pd.to_datetime(df[time_col]).dt.isocalendar().week

    plt.figure(figsize=(12, 6))
    for year in sorted(df['Year'].unique()):
        subset = df[df['Year'] == year]
        plt.plot(subset['Week'], subset[y_col], label=f'{year}')
    plt.title("Year-over-Year Weekly Sales")
    plt.legend()
    st.pyplot(plt)

def plot_monthly_trend(df, time_col, y_col):
    df['Year'] = pd.to_datetime(df[time_col]).dt.year
    df['Month'] = pd.to_datetime(df[time_col]).dt.month
    monthly = df.groupby(['Year', 'Month'])[y_col].sum().unstack(0)
    st.bar_chart(monthly)

def plot_weekly_trend(df, time_col, y_col):
    df['Week'] = pd.to_datetime(df[time_col]).dt.isocalendar().week
    weekly = df.groupby('Week')[y_col].sum()
    st.line_chart(weekly)

from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def ask_llm(question, df):
    preview = df.head(30).to_csv(index=False)
    system_prompt = "You are a time series data analyst. Answer user questions based on the CSV data provided."
    user_prompt = f"Data preview:\n{preview}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model="gpt-4.1-nano-2025-04-14",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()