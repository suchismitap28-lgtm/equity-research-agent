from flask import Flask, render_template, request, send_file, jsonify
import io, os, json, datetime as dt
from agents.report_agent import generate_report
from services.finance import fetch_quote, fetch_financials, quick_ratios_from_income_balance, dcf_quick
from services.search import news_headlines
from services.utils import OPENAI_API_KEY, mask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", has_key=bool(OPENAI_API_KEY), key_hint=mask(OPENAI_API_KEY))

@app.route("/generate", methods=["POST"])
def generate():
    company = request.form.get("company","").strip()
    ticker = request.form.get("ticker","").strip().upper()
    user_prompt = request.form.get("prompt","").strip()
    try:
        quote = fetch_quote(ticker) if ticker else {}
    except Exception:
        quote = {}
    try:
        financials = fetch_financials(ticker) if ticker else {}
    except Exception:
        financials = {}
    ratios = quick_ratios_from_income_balance(financials)
    # Attempt quick DCF from last known cash flow if available
    last_fcf = None
    try:
        import pandas as pd
        cf = financials.get("cashflow", [])
        if cf:
            df = pd.DataFrame(cf).set_index("item")
            # Try 'Free Cash Flow' row
            if "Free Cash Flow" in df.index:
                row = df.loc["Free Cash Flow"]
                for c in row.index:
                    val = row[c]
                    if pd.notnull(val):
                        last_fcf = float(val)
                        break
    except Exception:
        pass
    dcf = dcf_quick(last_fcf) if last_fcf else {"fair_value": None, "series": []}
    try:
        news = news_headlines(company or ticker, max_results=5, days=90) if (company or ticker) else []
    except Exception:
        news = []

    try:
        report_md = generate_report(company, ticker, user_prompt, quote, financials, ratios, news)
    except Exception as e:
        report_md = f"""## Error
There was a problem generating the report. Please check your API key and model.
**Details:** {e}
"""

    # Persist a simple JSON payload (for debugging / download)
    payload = {
        "company": company,
        "ticker": ticker,
        "prompt": user_prompt,
        "quote": quote,
        "ratios": ratios,
        "dcf": dcf,
        "news": news,
        "generated_at": dt.datetime.utcnow().isoformat() + "Z",
        "report_md": report_md,
    }

    return render_template("report.html", payload=json.dumps(payload, indent=2), md=report_md, company=company or ticker or "Equity Research Report")

@app.route("/download/html", methods=["POST"])
def download_html():
    html = request.form.get("html","")
    name = request.form.get("name","Equity_Research_Report").replace(" ","_")
    buf = io.BytesIO(html.encode("utf-8"))
    return send_file(buf, mimetype="text/html", as_attachment=True, download_name=f"{name}.html")

if __name__ == "__main__":
    app.run(debug=True)
