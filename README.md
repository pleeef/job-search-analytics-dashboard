# 🧩 Job Search Analytics Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://job-search-analytics-dashboard-za3ssytsoxv6u3ecf4k4wx.streamlit.app/)

An interactive analytics dashboard designed to track and optimize the job application process. This project treats the job search like a data pipeline, transforming raw application logs into actionable insights to improve conversion rates and strategy.

## 🔗 Live Demo
**[View the Live Dashboard Here](https://job-search-analytics-dashboard-za3ssytsoxv6u3ecf4k4wx.streamlit.app/)**

## 🚀 Key Features
- **Conversion Funnel:** Visualizes the journey from initial application to final offer (Applications → Replies → Interviews → Offers).
- **Activity Heatmap:** A GitHub-style intensity map to monitor application consistency and pace.
- **Weekday Effectiveness:** Analyzes which days of the week yield the highest response rates.
- **Response Time Analysis:** Statistical distribution of how long companies take to respond (Mean vs. Median).
- **Seniority Analysis:** Segmentation of applications by role level (Senior+, Middle, Junior).

## 🛠 Tech Stack
- **Python 3.10+**
- **Streamlit** (UI Framework & Deployment)
- **Plotly** (Interactive Visualizations: Heatmaps, Funnels, Donuts)
- **Pandas** (Data Wrangling & Feature Engineering)

## 📁 Project Structure
```text
├── app.py              # Main Streamlit application
├── src/
│   ├── data_prep.py    # Data cleaning and metric logic
│   └── charts.py       # Plotly visualization modules
├── data/
│   └── sample_data.csv # Anonymized demo dataset
└── notebooks/          # Exploratory Data Analysis (EDA)