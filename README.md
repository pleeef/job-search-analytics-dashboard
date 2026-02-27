# 📊 Job Search Analytics Dashboard

An analytics dashboard that tracks and analyzes a job application pipeline using real, continuously updated data (Google Sheets).

## What it includes
- Application funnel (applications → responses → interviews → offers)
- Weekly application volume heatmap
- Response time distribution (mean vs median)
- Weekday effectiveness analysis
- Seniority split (Senior+ / Middle / Junior)

## Data
**Do not commit your real dataset** (company names, positions, etc.) to a public repo.

This repo includes `data/sample_data.csv` as an example.  
To use your live data, publish your Google Sheet as CSV and paste the URL in the Streamlit sidebar.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Notebook
The original analysis notebook is in `notebooks/job_search_analytics.ipynb`.
