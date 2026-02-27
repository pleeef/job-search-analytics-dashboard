from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pandas as pd


DAYS_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _clean_status(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.replace({"nan": "", "None": "", "none": ""})
    return s


def get_level(title: str) -> str:
    """Classify a role title into Senior+ / Middle/Regular / Junior/Intern.

    Uses word-boundary matching to avoid accidental substring hits.
    """
    if title is None or (isinstance(title, float) and np.isnan(title)):  # type: ignore[arg-type]
        return "Middle/Regular"

    t = str(title).lower()

    senior_patterns = [
        r"\bsenior\b",
        r"\bsr\.?\b",
        r"\blead\b",
        r"\bprincipal\b",
        r"\bhead\b",
        r"\bmanager\b",
        r"\bii\b",  # e.g., "Analyst II" often implies more senior than entry
        r"\biii\b",
    ]
    junior_patterns = [
        r"\bjunior\b",
        r"\bjr\.?\b",
        r"\bintern\b",
        r"\btrainee\b",
        r"\bgraduate\b",
    ]

    if any(re.search(p, t) for p in senior_patterns):
        return "Senior+"
    if any(re.search(p, t) for p in junior_patterns):
        return "Junior/Intern"
    return "Middle/Regular"


def get_specialization(title: str) -> str:
    """Map a role title to a domain specialization for targeting analysis."""
    if title is None or (isinstance(title, float) and np.isnan(title)):  # type: ignore[arg-type]
        return "Unknown"

    t = str(title).lower()

    if any(k in t for k in ["marketing", "consumer", "crm", "d2c", "direct to consumer"]):
        return "Marketing & Consumer Analytics"
    if any(k in t for k in ["product", "growth", "experiment", "conversion"]):
        return "Product & Growth Analytics"
    if any(k in t for k in ["supply chain", "logistics"]):
        return "Supply Chain Analytics"
    if any(k in t for k in ["revenue", "pricing", "fp&a", "finance", "commercial", "strategic finance"]):
        return "Finance & Operations Analytics"
    if any(k in t for k in ["bi", "visualization", "reporting", "dashboard"]):
        return "BI & Reporting"
    if any(k in t for k in ["insight", "research"]):
        return "Insights & Research"
    if "data scientist" in t:
        return "Data Science"

    return "General Data Analytics"


def prepare_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Clean and enrich the job-search dataset.

    Expected columns: company, position, date_applied, response_date, status
    """
    df = df_raw.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    required = {"company", "position", "date_applied", "response_date", "status"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["date_applied"] = pd.to_datetime(df["date_applied"], errors="coerce")
    df["response_date"] = pd.to_datetime(df["response_date"], errors="coerce")
    df["status"] = _clean_status(df["status"])

    df = df[df["date_applied"].notna()].copy()

    # Core flags
    df["has_response"] = df["response_date"].notna() | (df["status"] != "")
    df["final_status"] = np.where(df["status"] == "", "No response", df["status"])

    # Response time (days) — keep negatives as NaN (data quality)
    rtd = (df["response_date"] - df["date_applied"]).dt.days
    df["response_time_days"] = rtd.where(rtd >= 0)

    # Time features
    df["week_commencing"] = df["date_applied"].dt.to_period("W").apply(lambda r: r.start_time)
    df["day_of_week"] = df["date_applied"].dt.day_name()

    # Response status (3 buckets)
    def categorize(row) -> str:
        if not row["has_response"]:
            return "No Feedback"
        if row["status"] in ["Interview", "Test task", "Offer"]:
            return "Active Interest"
        return "Rejection"

    df["response_status"] = df.apply(categorize, axis=1)

    # Role features
    df["level"] = df["position"].apply(get_level)
    df["specialization"] = df["position"].apply(get_specialization)

    return df


@dataclass
class Metrics:
    total_apps: int
    replied: int
    interviews: int
    offers: int
    search_duration_days: int
    response_rate_pct: float
    interview_rate_pct: float
    avg_response_time_days: Optional[float]
    median_response_time_days: Optional[float]


def compute_metrics(df: pd.DataFrame) -> Metrics:
    total_apps = int(len(df))
    replied = int(df["has_response"].sum())
    interviews = int(df["status"].isin(["Interview", "Test task"]).sum())
    offers = int(df["status"].isin(["Offer"]).sum())

    if total_apps:
        response_rate_pct = replied / total_apps * 100
        interview_rate_pct = interviews / total_apps * 100
    else:
        response_rate_pct = 0.0
        interview_rate_pct = 0.0

    if total_apps:
        search_duration_days = int((df["date_applied"].max() - df["date_applied"].min()).days)
    else:
        search_duration_days = 0

    rt = df["response_time_days"].dropna()
    avg_rt = float(rt.mean()) if len(rt) else None
    med_rt = float(rt.median()) if len(rt) else None

    return Metrics(
        total_apps=total_apps,
        replied=replied,
        interviews=interviews,
        offers=offers,
        search_duration_days=search_duration_days,
        response_rate_pct=response_rate_pct,
        interview_rate_pct=interview_rate_pct,
        avg_response_time_days=avg_rt,
        median_response_time_days=med_rt,
    )
