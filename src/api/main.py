from pathlib import Path
import csv

from fastapi import FastAPI


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="NIFTY 100 Financial Intelligence API",
    description="API for NIFTY 100 financial analysis and intelligence",
    version="1.0.0"
)


# =========================================================
# PROJECT PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
OUTPUT_DIR = BASE_DIR / "output"


# =========================================================
# CSV HELPER
# =========================================================

def read_csv_file(filename):
    file_path = OUTPUT_DIR / filename

    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "NIFTY 100 Financial Intelligence API is running"
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# API INFO
# =========================================================

@app.get("/api/info")
def api_info():
    return {
        "project": "NIFTY 100 Financial Intelligence",
        "version": "1.0.0",
        "status": "running"
    }


# =========================================================
# RANKINGS
# =========================================================

@app.get("/api/rankings")
def rankings():
    data = read_csv_file("company_rankings.csv")

    if data is None:
        return {
            "status": "error",
            "message": "company_rankings.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# METRICS
# =========================================================

@app.get("/api/metrics")
def metrics():
    data = read_csv_file("company_financial_metrics.csv")

    if data is None:
        return {
            "status": "error",
            "message": "company_financial_metrics.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# COMPANIES
# =========================================================

@app.get("/api/companies")
def companies():
    data = read_csv_file("company_financial_metrics.csv")

    if data is None:
        return {
            "status": "error",
            "message": "company_financial_metrics.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# TRENDS
# =========================================================

@app.get("/api/trends")
def trends():
    data = read_csv_file("analysis_parsed.csv")

    if data is None:
        return {
            "status": "error",
            "message": "analysis_parsed.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# SECTORS
# =========================================================

@app.get("/api/sectors")
def sectors():
    data = read_csv_file("company_financial_metrics.csv")

    if data is None:
        return {
            "status": "error",
            "message": "company_financial_metrics.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# PEERS
# =========================================================

@app.get("/api/peers")
def peers():
    file_path = OUTPUT_DIR / "peer_comparison.xlsx"

    if not file_path.exists():
        return {
            "status": "error",
            "message": "peer_comparison.xlsx not found"
        }

    return {
        "status": "success",
        "message": "Peer comparison file available",
        "file": str(file_path)
    }


# =========================================================
# CAPITAL
# =========================================================

@app.get("/api/capital")
def capital():
    data = read_csv_file("company_financial_metrics.csv")

    if data is None:
        return {
            "status": "error",
            "message": "company_financial_metrics.csv not found"
        }

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# =========================================================
# REPORTS
# =========================================================

@app.get("/api/reports")
def reports():
    file_path = OUTPUT_DIR / "financial_intelligence_insights.txt"

    if not file_path.exists():
        return {
            "status": "error",
            "message": "financial_intelligence_insights.txt not found"
        }

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    return {
        "status": "success",
        "content": content
    }