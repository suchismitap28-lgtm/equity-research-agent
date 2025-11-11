import sys, os
sys.path.append(os.path.dirname(__file__))
import streamlit as st
from agents.report_agent import generate_report
from services.finance import fetch_quote, fetch_financials, quick_ratios_from_income_balance, dcf_quick
from services.search import news_headlines
from services.utils import OPENAI_API_KEY
import pandas as pd
import json

st.set_page_config(page_title="Equity Research AI", layout="wide")

st.title("💼 AI-Powered Equity Research Report Generator")
st.caption("Generate detailed equity research reports using OpenAI + live financial data.")

# --- Sidebar ---
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TSLA, MSFT)", "")
company = st.sidebar.text_input("Company Name (optional)", "")
prompt = st.sidebar.text_area("Enter your custom prompt",
    "Write a detailed equity research report focusing on valuation, profitability, and future outlook."
)

generate = st.sidebar.button("Generate Report")

if not OPENAI_API_KEY:
    st.warning("⚠️ No OpenAI API key found. Please set it in your environment or secrets.")
else:
    st.sidebar.success("✅ API Key Loaded")

# --- Main Output ---
if generate:
    if not ticker:
        st.error("Please enter at least a stock ticker.")
    else:
        with st.spinner("Fetching data and generating report... ⏳"):
            try:
                quote = fetch_quote(ticker)
                financials = fetch_financials(ticker)
                ratios = quick_ratios_from_income_balance(financials)
                dcf = dcf_quick(1_000_000)  # example input
                news = news_headlines(company or ticker, max_results=5)

                report_md = generate_report(company, ticker, prompt, quote, financials, ratios, news)

                st.subheader(f"📊 Equity Research Report for {company or ticker}")
                st.markdown(report_md)
                
                st.download_button("📥 Download Report", report_md, file_name=f"{ticker}_report.md")
                
                with st.expander("View Debug Info"):
                    st.json({
                        "ticker": ticker,
                        "quote": quote,
                        "ratios": ratios,
                        "dcf": dcf,
                        "news": news,
                    })
            except Exception as e:
                st.error(f"❌ Error while generating report: {e}")
