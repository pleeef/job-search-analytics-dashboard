import pandas as pd
import streamlit as st
import os

from src.data_prep import prepare_data, compute_metrics

from src.charts import (
    fig_overview,
    fig_minimalistic_funnel,
    fig_response_time,
    fig_weekday_effectiveness,
    fig_success_by_level
)

st.set_page_config(page_title="Job Search Analytics", layout="wide")
st.title("Job Search Analytics Dashboard")

DATA_PATH = "data/job-search-analytics.xlsx" # local Excel with real data
SAMPLE_PATH = "data/sample_data.csv"         # Anonymized file for Git

df_raw = None

if os.path.exists(DATA_PATH):
    df_raw = pd.read_excel(DATA_PATH)
elif os.path.exists(SAMPLE_PATH):
    df_raw = pd.read_csv(SAMPLE_PATH)
else:
    st.error("Data files not found in 'data/' folder!")
    st.stop()

try:
    df = prepare_data(df_raw)
except Exception as e:
    st.error(f"Data preparation failed: {e}")
    st.stop()

m = compute_metrics(df)
dff = df.copy()
mf = compute_metrics(dff)

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Applications", mf.total_apps)
k2.metric("Responses", mf.replied, f"{mf.response_rate_pct:.1f}%")
k3.metric("Interviews", mf.interviews, f"{mf.interview_rate_pct:.1f}%")
k4.metric("Median response (days)", "-" if mf.median_response_time_days is None else f"{mf.median_response_time_days:.0f}")
k5.metric("Search duration (days)", mf.search_duration_days)

st.plotly_chart(fig_overview(dff, mf), use_container_width=True)

c1, c2 = st.columns([3, 2]) 

with c1:
    # Здесь будет воронка
    st.plotly_chart(fig_minimalistic_funnel(mf), use_container_width=True)
with c2:
    # Здесь будет кольцевая диаграмма
    st.plotly_chart(fig_success_by_level(dff), use_container_width=True)

st.plotly_chart(fig_response_time(dff, mf), use_container_width=True)

st.plotly_chart(fig_weekday_effectiveness(dff), use_container_width=True)
