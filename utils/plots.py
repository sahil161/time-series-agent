import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

def plot_yearly_trend(df, time_col, target_col):
    df = df.copy()
    df["Year"] = df[time_col].dt.year
    df["Week"] = df[time_col].dt.isocalendar().week

    # Group by year and week, sum sales
    grouped = df.groupby(["Year", "Week"])[target_col].sum().reset_index()

    # Plotting
    plt.figure(figsize=(12, 6))
    for year in sorted(grouped["Year"].unique()):
        year_data = grouped[grouped["Year"] == year]
        plt.plot(year_data["Week"], year_data[target_col], marker='o', label=str(year))

    plt.title("Year-over-Year Weekly Trend")
    plt.xlabel("Week Number")
    plt.ylabel("Total Sales")
    plt.legend(title="Year")
    plt.grid(True)
    st.pyplot(plt)

def plot_monthly_trend(df, time_col, target_col):
    df = df.copy()
    df["Year"] = df[time_col].dt.year
    df["Month"] = df[time_col].dt.month

    # Group by year and month, sum sales
    grouped = df.groupby(["Year", "Month"])[target_col].sum().reset_index()

    # Plotting
    plt.figure(figsize=(12, 6))
    for year in sorted(grouped["Year"].unique()):
        year_data = grouped[grouped["Year"] == year]
        plt.plot(year_data["Month"], year_data[target_col], marker='o', label=str(year))

    plt.title("Year-over-Year Monthly Trend")
    plt.xlabel("Month Number")
    plt.ylabel("Total Sales")
    plt.xticks(range(1, 13))
    plt.legend(title="Year")
    plt.grid(True)
    st.pyplot(plt)

def plot_weekly_trend(df, time_col, y_col):
    df['Week'] = pd.to_datetime(df[time_col]).dt.isocalendar().week
    weekly = df.groupby('Week')[y_col].sum()
    st.line_chart(weekly)
