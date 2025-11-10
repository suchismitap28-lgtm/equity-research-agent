import datetime as dt
import pandas as pd
import numpy as np
import yfinance as yf

def fetch_quote(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    info = t.fast_info or {}
    hist = t.history(period="5y", interval="1d")
    return {
        "ticker": ticker.upper(),
        "currency": getattr(t, "fast_info", {}).get("currency", "USD"),
        "last_price": float(info.get("last_price") or info.get("lastPrice") or np.nan),
        "market_cap": float(info.get("market_cap") or info.get("marketCap") or np.nan),
        "hist": hist.reset_index().to_dict(orient="records") if isinstance(hist, pd.DataFrame) else [],
    }

def fetch_financials(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    fin = {}
    try:
        fin["income_stmt"] = t.income_stmt.reset_index().rename(columns={"index":"item"}).to_dict(orient="records")
    except Exception:
        fin["income_stmt"] = []
    try:
        fin["balance_sheet"] = t.balance_sheet.reset_index().rename(columns={"index":"item"}).to_dict(orient="records")
    except Exception:
        fin["balance_sheet"] = []
    try:
        fin["cashflow"] = t.cashflow.reset_index().rename(columns={"index":"item"}).to_dict(orient="records")
    except Exception:
        fin["cashflow"] = []
    return fin

def quick_ratios_from_income_balance(financials: dict) -> dict:
    import pandas as pd
    out = {}
    try:
        bs = pd.DataFrame(financials.get("balance_sheet", []))
        is_ = pd.DataFrame(financials.get("income_stmt", []))
        if not bs.empty and not is_.empty:
            # Grab latest column with numeric data
            def latest_value(df, item):
                row = df[df["item"].str.lower()==item.lower()]
                row = row.drop(columns=["item"], errors="ignore")
                if row.empty:
                    return None
                # Take the first non-null among sorted columns
                for c in row.columns:
                    v = row[c].values[0]
                    if pd.notnull(v):
                        return float(v)
                return None
            sales = latest_value(is_, "Total Revenue") or latest_value(is_, "TotalRevenue")
            net_income = latest_value(is_, "Net Income") or latest_value(is_, "NetIncome")
            total_assets = latest_value(bs, "Total Assets") or latest_value(bs, "TotalAssets")
            total_equity = latest_value(bs, "Stockholders Equity") or latest_value(bs, "Total Stockholder Equity") or latest_value(bs, "TotalEquity")
            if sales and total_assets:
                out["asset_turnover"] = sales/total_assets
            if net_income and sales:
                out["net_margin"] = net_income/sales
            if net_income and total_equity and total_equity != 0:
                out["roe"] = net_income/total_equity
    except Exception:
        pass
    return out

def dcf_quick(last_fcf: float, growth_years: int=5, growth_rate: float=0.08, discount_rate: float=0.10, terminal_growth: float=0.025) -> dict:
    """Very rough DCF using last known FCF per share or total FCF (user context)."""
    if last_fcf is None:
        return {"fair_value": None, "series": []}
    series = []
    fcf = last_fcf
    pv = 0.0
    for y in range(1, growth_years+1):
        fcf *= (1.0 + growth_rate)
        pv += fcf / ((1.0 + discount_rate) ** y)
        series.append({"year": y, "fcf": fcf, "pv": fcf / ((1.0 + discount_rate) ** y)})
    terminal = (fcf * (1.0 + terminal_growth)) / (discount_rate - terminal_growth)
    terminal_pv = terminal / ((1.0 + discount_rate) ** growth_years)
    fair = pv + terminal_pv
    return {"fair_value": fair, "series": series, "terminal_pv": terminal_pv}
