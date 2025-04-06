import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from helpers import plot_trends, generate_contribution_table
from helpers import count_unique_intersections

st.set_page_config(page_title="🧠 Forecast Parameter Setup", layout="wide")
st.title("🧠 Forecast Configurator")

# Initialize step state
if 'step' not in st.session_state:
    st.session_state.step = 1

# Step 1: Upload Files
if st.session_state.step == 1:
    st.subheader("📤 Upload Files")

    uploaded_df_actual = st.file_uploader("📦 Upload your **df_actual** file (CSV)", type=["csv"])
    uploaded_df_time = st.file_uploader("🕒 Upload your **df_time** file (CSV)", type=["csv"])

    if uploaded_df_actual and uploaded_df_time:
        st.session_state.df = pd.read_csv(uploaded_df_actual)
        st.session_state.df_time = pd.read_csv(uploaded_df_time)
        st.success("✅ Both files uploaded successfully.")
        st.session_state.step = 2
        st.rerun()


# Step 2: Collect Parameters
elif st.session_state.step == 2:
    df = st.session_state.df

    st.subheader("🛠️ Parameter Setup")

    st.session_state.col_version = st.selectbox("🗂️ Select column for Version", df.columns)
    st.session_state.version_name = st.selectbox("📌 Select version name", sorted(df[st.session_state.col_version].dropna().unique()))
    st.session_state.col_time = st.selectbox("🕒 Select the column representing time", df.columns)
    st.session_state.col_sales = st.selectbox("📊 Select column for Sales", df.columns)

    forecast_level = st.multiselect(
        "🧩 Select Forecast Level columns (excluding version column)",
        [col for col in df.columns if col != st.session_state.col_version]
    )
    st.session_state.forecast_level = [st.session_state.col_version] + forecast_level
    
    # ✅ Show number of unique intersections (excluding time column)
    if forecast_level:
        try:
            count= count_unique_intersections(
                df,
                col_version=st.session_state.col_version,
                col_groupby=forecast_level,
                version_name=st.session_state.version_name
            )
            st.markdown(f"🔍 **Number of unique intersections at the selected forecast level:** `{count}`")
        except Exception as e:
            st.error(f"Error counting intersections: {e}")

    time_values = pd.to_datetime(df[st.session_state.col_time].dropna().unique(), dayfirst=True, errors='coerce')
    time_values = sorted([d.strftime("%d-%m-%Y") for d in time_values if pd.notnull(d)])
    st.session_state.history_end_week = st.selectbox("📅 Select history end week", time_values)

    st.session_state.forecast_period = st.number_input("🔮 Enter number of forecast periods", min_value=1, max_value=260)

    if st.button("✅ Confirm Parameters"):
        st.session_state.step = 3
        st.rerun()

# Step 3: Action Selection
elif st.session_state.step == 3:
    st.subheader("🚀 What would you like to do?")
    st.write("Choose one of the options below:")

    if st.button("📈 Plot Trends"):
        st.session_state.step = 4
        st.rerun()

    if st.button("📋 Generate Contribution Table"):
        st.session_state.step = 5
        st.rerun()

    if st.button("💬 Give Feedback"):
        st.session_state.step = 6
        st.rerun()

# Step 4: Plot Trends
elif st.session_state.step == 4:
    st.subheader("📊 Sales Trends")
    with st.spinner("Generating plots..."):
        try:
            plot_trends(
                st.session_state.df,
                st.session_state.col_sales,
                st.session_state.col_version,
                st.session_state.col_time,
                st.session_state.version_name,
                in_streamlit=True
            )
            st.success("✅ Plots generated successfully!")
        except Exception as e:
            st.error(f"❌ Error while plotting trends: {e}")

    if st.button("🔙 Back to Actions"):
        st.session_state.step = 3
        st.rerun()

# Step 5: Contribution Table
elif st.session_state.step == 5:
    st.subheader("📊 Contribution Table")

    df = st.session_state.df
    col_sales = st.session_state.col_sales

    col_contribution = st.selectbox(
        "📂 Select column for contribution analysis",
        [col for col in df.columns if col != col_sales],
        key="contrib_col_selector"
    )

    if "last_rendered_col" not in st.session_state:
        st.session_state.last_rendered_col = None
    if "df_contribution" not in st.session_state:
        st.session_state.df_contribution = None

    if col_contribution != st.session_state.last_rendered_col:
        with st.spinner(f"Calculating contribution for `{col_contribution}`..."):
            try:
                df_contribution = generate_contribution_table(df, col_contribution, col_sales)
                st.session_state.df_contribution = df_contribution
                st.session_state.last_rendered_col = col_contribution
                st.success(f"✅ Contribution table for `{col_contribution}` generated!")
            except Exception as e:
                st.error(f"❌ Error generating contribution table: {e}")

    if st.session_state.df_contribution is not None:
        st.dataframe(st.session_state.df_contribution)

    if st.button("🔁 Reset Contribution View"):
        del st.session_state["contrib_col_selector"]
        st.session_state.last_rendered_col = None
        st.session_state.df_contribution = None
        st.session_state.step = 3
        st.rerun()

    if st.button("🔙 Back to Actions"):
        st.session_state.step = 3
        st.rerun()

# Step 6: Feedback
elif st.session_state.step == 6:
    st.subheader("📝 We Value Your Feedback!")

    feedback_text = st.text_area("❓ What is missing or what would you like us to improve?", placeholder="e.g., Add more models, show MAPE, include export feature...")

    if st.button("📩 Submit Feedback"):
        if feedback_text.strip():
            feedback_df = pd.DataFrame([{
                "timestamp": pd.Timestamp.now(),
                "feedback": feedback_text.strip()
            }])

            feedback_df.to_csv("feedback.csv", mode='a', header=not pd.io.common.file_exists("feedback.csv"), index=False)
            st.success("✅ Thank you! Your feedback has been recorded.")
            st.session_state.step = 3
            st.rerun()
        else:
            st.warning("⚠️ Please enter some feedback before submitting.")

    if st.button("🔙 Back to Actions"):
        st.session_state.step = 3
        st.rerun()