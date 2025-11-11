import streamlit as st
from fpdf import FPDF
from agents.report_agent import generate_report
from services.finance import fetch_quote, fetch_financials, quick_ratios_from_income_balance, dcf_quick
from services.search import news_headlines
from services.utils import OPENAI_API_KEY
import io
import pandas as pd

st.set_page_config(page_title="Equity Research AI", layout="wide")

st.title("💼 AI-Powered Equity Research Report Generator")
st.caption("Generate detailed, AI-driven equity research reports with live financial data.")

# --- Sidebar Input ---
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TATAMOTORS.NS)", "")
company = st.sidebar.text_input("Company Name (optional)", "")
prompt = st.sidebar.text_area(
    "Enter your custom prompt",
    "Write a detailed equity research report focusing on valuation, profitability, and future outlook."
)

generate = st.sidebar.button("Generate Report")

if not OPENAI_API_KEY:
    st.warning("⚠️ No OpenAI API key found. Please set it in your environment or Streamlit Secrets.")
else:
    st.sidebar.success("✅ API Key Loaded")

# --- Function to Create PDF ---
def create_pdf(report_text, company_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, report_text)
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# --- Main Content ---
if generate:
    if not ticker:
        st.error("Please enter a stock ticker symbol.")
    else:
        with st.spinner("Generating your report... ⏳"):
            try:
                quote = fetch_quote(ticker)
                financials = fetch_financials(ticker)
                ratios = quick_ratios_from_income_balance(financials)
                news = news_headlines(company or ticker, max_results=5)

                report_md = generate_report(company, ticker, prompt, quote, financials, ratios, news)

                # Display report
                st.subheader(f"📊 Equity Research Report for {company or ticker}")
                st.markdown(report_md)

                # Generate PDF
                pdf_file = create_pdf(report_md, company or ticker)

                # Download Button
                st.download_button(
                    label="📄 Download Report as PDF",
                    data=pdf_file,
                    file_name=f"{company or ticker}_Equity_Research_Report.pdf",
                    mime="application/pdf"
                )

                with st.expander("View Debug Info"):
                    st.json({
                        "ticker": ticker,
                        "quote": quote,
                        "ratios": ratios,
                        "news": news,
                    })

            except Exception as e:
                st.error(f"❌ Error generating report: {e}")
