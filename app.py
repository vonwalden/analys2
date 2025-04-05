Aktie Vardering Med Poang
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
32
33
34
35
36
37
38
39
40
41
42
43
44
45
46
47
48
49
50
51
52
53
54
55
56
57
58
59
60
61
62
63
64
65
66
67
68
69
70
71
72
73
74
75
76
77
78
79
80
81
82
83
84
85
86
87
88
89
90
91
92
93
94
95
96
97
98
99
100
101
102
103
104
105
106
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
                "Tillväxt (%)": round(growth * 100, 1) if growth is not None else None,
                "Marginal (%)": round(margin * 100, 1) if margin is not None else None,
                "FCF (MUSD)": round(fcf / 1e6, 1) if fcf is not None else None,
                "ROE (%)": round(roe * 100, 1) if roe is not None else None,
                "PEG": peg,
                "D/E": round(de, 2) if de is not None else None,
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
            return "background-color: #c6f5c6; font-weight: bold"
        elif score >= 5:
            return "background-color: #fff3b0;"
        else:
            return "background-color: #f9c0c0;"

    # Använd formatters som hanterar None-värden
    def safe_format(val, fmt):
        return fmt.format(val) if pd.notnull(val) else "–"

    styled = df_sorted.style.applymap(highlight, subset=["Poäng (1-10)"]).format({
        "EPS": lambda x: safe_format(x, "{:.2f}"),
        "Beta": lambda x: safe_format(x, "{:.2f}"),
        "P/S": lambda x: safe_format(x, "{:.2f}"),
        "Tillväxt (%)": lambda x: safe_format(x, "{:.1f}"),
        "Marginal (%)": lambda x: safe_format(x, "{:.1f}"),
        "FCF (MUSD)": lambda x: safe_format(x, "{:.1f}"),
        "ROE (%)": lambda x: safe_format(x, "{:.1f}"),
        "PEG": lambda x: safe_format(x, "{:.2f}"),
        "D/E": lambda x: safe_format(x, "{:.2f}"),
        "Utdelning (%)": lambda x: safe_format(x, "{:.2f}")
    })

    st.dataframe(styled, use_container_width=True)

    st.subheader("🔹 Topp 5 aktier enligt poängsystem")
    st.table(df_sorted[['Namn', 'Ticker', 'Poäng (1-10)']].head(5))

