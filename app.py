import streamlit as st
from fpdf import FPDF
import io
import os

from agents.report_agent import generate_report
from services.finance import fetch_quote, fetch_financials, quick_ratios_from_income_balance, dcf_quick
from services.search import news_headlines
from services.utils import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, show_current_llm_config

st.set_page_config(page_title="Equity Research AI", layout="wide")

# ----------------------------------------------------------------------
# 🌐 APP HEADER
# ----------------------------------------------------------------------
st.title("📊 AI-Powered Equity Research Report Generator")
st.caption("Generate professional equity research reports using AI models like Llama 3 (Groq) with live financial data.")

# Show current LLM configuration for transparency
st.info(show_current_llm_config())

# ----------------------------------------------------------------------
# ⚙️ SIDEBAR CONFIGURATION
# ----------------------------------------------------------------------
st.sidebar.header("Configuration")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g. AAPL, TATAMOTORS.NS)", "")
company = st.sidebar.text_input("Company Name (optional)", "")
prompt = st.sidebar.text_area(
    "Custom Prompt",
    "Write a detailed equity research report focusing on valuation, profitability, and future outlook."
)

generate = st.sidebar.button("Generate Report")

if not OPENAI_API_KEY:
    st.warning("⚠️ No API key found. Please add it in Streamlit Secrets.")
else:
    st.sidebar.success("✅ API Key Loaded")

# ----------------------------------------------------------------------
# 🧾 PDF CREATION (Unicode-compatible)
# ----------------------------------------------------------------------
def create_pdf(report_text, company_name):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Use Unicode font to support emojis and special characters
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    if os.path.exists(font_path):
        pdf.add_font("DejaVu", "", font_path, uni=True)
        pdf.set_font("DejaVu", size=12)
    else:
        pdf.set_font("Arial", size=12)

    # Clean text to avoid unsupported characters
    safe_text = report_text.encode("utf-8", "ignore").decode("utf-8")
    pdf.multi_cell(0, 10, safe_text)

    # Return PDF as bytes
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# ----------------------------------------------------------------------
# 🚀 MAIN REPORT GENERATION LOGIC
# ----------------------------------------------------------------------
if generate:
    if not ticker:
        st.error("Please enter a stock ticker symbol.")
    else:
        with st.spinner("Generating your report... ⏳"):
            try:
                # Fetch financial data
                quote = fetch_quote(ticker)
                financials = fetch_financials(ticker)
                ratios = quick_ratios_from_income_balance(financials)
                news = news_headlines(company or ticker, max_results=5)

                # Generate AI report
                report_md = generate_report(company, ticker, prompt, quote, financials, ratios, news)

                # Display result
                st.subheader(f"📄 Equity Research Report for {company or ticker}")
                st.markdown(report_md)

                # Export PDF
                pdf_file = create_pdf(report_md, company or ticker)

                # Download button
                st.download_button(
                    label="📥 Download Report as PDF",
                    data=pdf_file,
                    file_name=f"{company or ticker}_Equity_Research_Report.pdf",
                    mime="application/pdf"
                )

                # Debug info
                with st.expander("🔍 View Debug Info"):
                    st.json({
                        "Ticker": ticker,
                        "Quote": quote,
                        "Ratios": ratios,
                        "News Count": len(news)
                    })

            except Exception as e:
                st.error(f"❌ Error generating report: {e}")

# ----------------------------------------------------------------------
# 🧠 FOOTER
# ----------------------------------------------------------------------
st.markdown("---")
st.caption("⚙️ Powered by Llama 3 (Groq) | Developed for AI-driven Financial Insights")
