import pandas as pd
from itertools import product
import matplotlib.pyplot as plt
import streamlit as st

def fill_missing_weeks(df, date_col, target_col, key_cols):
    # Ensure datetime format
    df[date_col] = pd.to_datetime(df[date_col])

    # Aggregate in case of duplicate keys for same week
    df = df.groupby(key_cols + [date_col], as_index=False)[target_col].sum()

    filled_frames = []

    for key_vals, group_df in df.groupby(key_cols):
        if not isinstance(key_vals, tuple):
            key_vals = (key_vals,)
        
        # Determine date range for this key
        min_date = group_df[date_col].min()
        max_date = group_df[date_col].max()
        full_weeks = pd.date_range(start=min_date, end=max_date, freq='W-SUN')

        # Create full frame
        temp_df = pd.DataFrame({date_col: full_weeks})
        for col, val in zip(key_cols, key_vals):
            temp_df[col] = val
        temp_df[target_col] = 0  # initialize with 0 sales

        # Merge actual data
        merged = pd.merge(temp_df, group_df, on=key_cols + [date_col], how='left', suffixes=('_fill', ''))
        merged[target_col] = merged[target_col].fillna(merged[f"{target_col}_fill"])
        merged = merged.drop(columns=[f"{target_col}_fill"])

        filled_frames.append(merged)

    df_filled = pd.concat(filled_frames, ignore_index=True)
    return df_filled



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
