import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Aktievärdering med Poäng", layout="wide")
st.title("📊 Aktievärdering med Poängsystem (1–10)")

st.markdown("""
Denna app analyserar aktier med nyckeltal och sätter poäng 1–10 baserat på:
- EPS > 2
- Beta mellan 0.7 och 1.3
- P/S < 4
- Revenue Growth > 5%
- Operating Margin > 15%
- Free Cash Flow > 0
- ROE > 10%
- PEG < 1.5
- D/E < 1.0
- Dividend Yield > 2%
""")

symbols = st.text_input("Ange ticker-symboler (komma-separerade):", "AAPL,MSFT,TSLA,AZN.ST")
tickers = [s.strip() for s in symbols.split(",") if s.strip() != ""]

@st.cache_data(show_spinner=False)
def fetch_with_scores(tickers):
    rows = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            eps = info.get("trailingEps")
            beta = info.get("beta")
            ps = info.get("priceToSalesTrailing12Months")
            growth = info.get("revenueGrowth")
            margin = info.get("operatingMargins")
            fcf = info.get("freeCashflow")
            roe = info.get("returnOnEquity")
            peg = info.get("pegRatio")
            de = info.get("debtToEquity")
            dividend = info.get("dividendYield")

            score = 0
            score += 1 if eps and eps > 2 else 0
            score += 1 if beta and 0.7 <= beta <= 1.3 else 0
            score += 1 if ps and ps < 4 else 0
            score += 1 if growth and growth > 0.05 else 0
            score += 1 if margin and margin > 0.15 else 0
            score += 1 if fcf and fcf > 0 else 0
            score += 1 if roe and roe > 0.10 else 0
            score += 1 if peg and peg < 1.5 else 0
            score += 1 if de and de < 1.0 else 0
            score += 1 if dividend and dividend * 100 > 2 else 0

            rows.append({
                "Ticker": ticker,
                "Namn": info.get("shortName", ticker),
                "Poäng (1-10)": score,
                "EPS": eps,
                "Beta": beta,
                "P/S": ps,
                "Tillväxt (%)": round(growth * 100, 1) if growth else None,
                "Marginal (%)": round(margin * 100, 1) if margin else None,
                "FCF (MUSD)": round(fcf / 1e6, 1) if fcf else None,
                "ROE (%)": round(roe * 100, 1) if roe else None,
                "PEG": peg,
                "D/E": round(de, 2) if de else None,
                "Utdelning (%)": round(dividend * 100, 2) if dividend else 0
            })
        except Exception as e:
            st.warning(f"Fel vid hämtning av data för {ticker}: {e}")
    return pd.DataFrame(rows)

if st.button("Analysera"):
    df = fetch_with_scores(tickers)
    st.subheader("🔢 Bolagsbetyg")
    df_sorted = df.sort_values(by="Poäng (1-10)", ascending=False).reset_index(drop=True)

    def highlight(score):
        if score >= 8:
            return "background-color: #c6f5c6; font-weight: bold"  # Grönt
        elif score >= 5:
            return "background-color: #fff3b0;"  # Gult
        else:
            return "background-color: #f9c0c0;"  # Rött

    styled = df_sorted.style.applymap(highlight, subset=["Poäng (1-10)"]).format({
        "EPS": "{:.2f}",
        "Beta": "{:.2f}",
        "P/S": "{:.2f}",
        "Tillväxt (%)": "{:.1f}",
        "Marginal (%)": "{:.1f}",
        "FCF (MUSD)": "{:.1f}",
        "ROE (%)": "{:.1f}",
        "PEG": "{:.2f}",
        "D/E": "{:.2f}",
        "Utdelning (%)": "{:.2f}"
    })

    st.dataframe(styled, use_container_width=True)

    st.subheader("🔹 Topp 5 aktier enligt poängsystem")
    st.table(df_sorted[['Namn', 'Ticker', 'Poäng (1-10)']].head(5))
