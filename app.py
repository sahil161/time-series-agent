import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="📅 Time Series Viewer", layout="wide")
st.title("📅 Time Series Visualizer")

# Step 1: Upload
uploaded_file = st.file_uploader("📤 Upload your time series CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    st.subheader("🔍 Preview of Uploaded Data")
    st.write("**First 2 rows:**")
    st.write(df.head(2))
    st.write("**Last 2 rows:**")
    st.write(df.tail(2))

    # Step 2: Column selection
    time_col = st.selectbox("🕒 Select the date/time column", df.columns)
    value_col = st.selectbox("📊 Select the value column", df.columns)

    # Step 3: Ask for frequency
    frequency = st.radio("📆 What is the data frequency?", ["Weekly", "Monthly"], horizontal=True)

    # Step 4: Parse datetime
    try:
        df[time_col] = pd.to_datetime(df[time_col], dayfirst=True, errors='raise')
    except Exception as e:
        st.error(f"❌ Could not parse dates: {e}")
        st.stop()

    # Rename for consistency
    df = df[[time_col, value_col]].rename(columns={time_col: "ds", value_col: "y"})

    # Step 5: Plot
    st.subheader("📉 Time Series Plot")
    fig, ax = plt.subplots()
    ax.plot(df["ds"], df["y"], marker='o', linestyle='-')
    ax.set_title(f"{frequency} Time Series")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    st.pyplot(fig)
