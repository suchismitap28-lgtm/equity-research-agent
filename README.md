# Equity Research Agent (Flask + OpenAI + yfinance)

A simple, full‑stack Flask web app that generates AI‑assisted equity research reports from a natural‑language prompt.

## Features
- Web UI form to enter: company/ticker + prompt + optional constraints
- Pulls market/financial data with `yfinance`
- Optional quick news/context from the web using DuckDuckGo (no API key needed)
- Crafts a structured research report (Summary → Business → Industry → Financials → Valuation → Risks → Outlook)
- Renders as a clean HTML page (with sections, charts, and references)
- One-click “Download HTML”
- Modular code: `agents/` for AI logic, `services/` for data fetching
- Works with OpenAI or any OpenAI‑compatible endpoint (via env vars)

## Quickstart
1. **Install** (Python 3.10+ recommended):
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables** (copy `.env.example` to `.env` and edit):
   - `OPENAI_API_KEY`: your OpenAI key
   - Optional for non‑OpenAI providers: `OPENAI_BASE_URL`, `OPENAI_MODEL`

3. **Run**:
   ```bash
   flask --app app run --debug
   ```
   App will start at `http://127.0.0.1:5000/`

4. **Use it**
   - Enter a **Ticker** (e.g., `AAPL`) and/or **Company name**.
   - Enter a **Prompt** (e.g., “write an equity research report focusing on FY2024 margins, risks, and a DCF fair value range”).
   - Click **Generate Report**.

## Notes
- **Ticker is recommended.** If you only provide a company name, the app will attempt a quick ticker guess, but accuracy depends on search results.
- PDF export is not included by default to avoid platform dependencies; use your browser’s “Print → Save as PDF” or install a converter.
- News scraping is lightweight (DuckDuckGo) to avoid API costs; replace with your preferred provider if you need richer news.
- All LLM prompts are in `agents/report_agent.py`. Tune structure, tone, or section weights there.

## Project Structure
```
equity-research-agent/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── agents/
│   └── report_agent.py
├── services/
│   ├── finance.py
│   ├── search.py
│   └── utils.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── report.html
└── static/
    └── style.css
```

## Security
- Never commit your `.env` with keys.
- Requests to news and finance are best‑effort and may be blocked by some networks.

## License
MIT
