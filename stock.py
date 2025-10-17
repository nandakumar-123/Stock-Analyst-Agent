import os
from dotenv import load_dotenv
import openai
import streamlit as st
import yfinance as yf
from datetime import datetime
from ta.momentum import RSIIndicator
from ta.trend import MACD

# -------------------
# Load API Key
# -------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# -------------------
# Streamlit page config
# -------------------
st.set_page_config(page_title="🌞 AI Stock Analyzer", layout="wide")

# -------------------
# Custom CSS for red theme
# -------------------
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #ffcccc, #ff9999, #ff6666);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    font-family: 'Helvetica', sans-serif;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Red glowing title */
.title {
    font-size: 3.5rem;
    font-weight: 900;
    color: #ff4d4d;
    text-align: center;
    text-shadow: 2px 2px 12px rgba(255,77,77,0.7), 0 0 20px rgba(255,77,77,0.5);
}

/* Red glowing subtitle */
.subtitle {
    font-size: 1.5rem;
    font-weight: 600;
    color: #ff6666;
    text-align: center;
    margin-bottom: 30px;
    text-shadow: 1px 1px 10px rgba(255,102,102,0.7);
}

/* Metric cards */
.metric-card {
    background: rgba(255,255,255,0.95);
    padding: 20px;
    border-radius: 20px;
    box-shadow: 4px 4px 25px rgba(0,0,0,0.25);
    margin-bottom: 20px;
    transition: transform 0.2s;
}
.metric-card:hover {
    transform: translateY(-5px);
}

/* Recommendation banners */
.recommendation {
    font-size: 1.8rem;
    font-weight: bold;
    padding: 15px;
    border-radius: 15px;
    text-align: center;
    color: #fff;
    box-shadow: 3px 3px 20px rgba(0,0,0,0.3);
}
.buy { background: linear-gradient(90deg, #28a745, #85e085); }
.hold { background: linear-gradient(90deg, #ffc107, #ffe08c); color: #000; }
.sell { background: linear-gradient(90deg, #dc3545, #ff7b7b); }

/* Streamlit button styling */
.stButton>button {
    background-color: #ff4d4d;
    color: #fff;
    font-weight: bold;
    border-radius: 12px;
}
.stButton>button:hover {
    background-color: #ff6666;
}
</style>
""", unsafe_allow_html=True)

# -------------------
# Header
# -------------------
st.markdown('<div class="title">🌞 AI Stock Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze stocks with technical, fundamental & AI insights</div>', unsafe_allow_html=True)

# -------------------
# User input
# -------------------
ticker = st.text_input("", placeholder="e.g., AAPL").upper()
analyze = st.button("Analyze", type="primary")

# -------------------
# Helper functions
# -------------------
def fetch_data(symbol):
    tk = yf.Ticker(symbol)
    hist = tk.history(period="1y", interval="1d", auto_adjust=True)
    fast = tk.fast_info or {}
    return hist, fast

def compute_indicators(hist):
    close = hist["Close"]
    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()
    rsi = RSIIndicator(close).rsi()
    macd_obj = MACD(close)
    macd = macd_obj.macd()
    macd_signal = macd_obj.macd_signal()
    return {
        "last_price": float(close.iloc[-1]),
        "sma50": float(sma50.iloc[-1]),
        "sma200": float(sma200.iloc[-1]),
        "rsi": float(rsi.iloc[-1]),
        "macd": float(macd.iloc[-1]),
        "macd_signal": float(macd_signal.iloc[-1]),
    }

def extract_fundamentals(fast):
    def safe(k): return float(fast.get(k)) if fast.get(k) else None
    return {
        "market_cap": safe("market_cap"),
        "pe_ratio": safe("trailing_pe"),
        "forward_pe": safe("forward_pe"),
        "pb_ratio": safe("price_to_book"),
        "dividend_yield": safe("dividend_yield"),
    }

def ask_openai(payload):
    prompt = f"""
You are a professional stock analyst. Recommend one of: BUY, HOLD, SELL.
Respond in JSON:
{{
"action": "BUY" | "HOLD" | "SELL",
"confidence": 0-100,
"technical_summary": "...",
"fundamental_summary": "...",
"risks": ["...", "..."],
"notes": "..."
}}
DATA:
{payload}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a disciplined equity research analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        msg = response["choices"][0]["message"]["content"]
        start = msg.find("{")
        end = msg.rfind("}")
        return eval(msg[start:end+1])
    except Exception as e:
        return {"error": str(e), "raw": msg if 'msg' in locals() else ""}

# -------------------
# Run analysis
# -------------------
if analyze and ticker:
    with st.spinner(f"Analyzing {ticker}..."):
        hist, fast = fetch_data(ticker)
        if hist.empty:
            st.error("No historical data found for this symbol.")
        else:
            technicals = compute_indicators(hist)
            fundamentals = extract_fundamentals(fast)

            st.subheader("📊 Technical & Fundamental Indicators")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.json(technicals)
                st.markdown('</div>', unsafe_allow_html=True)
            with c2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.json(fundamentals)
                st.markdown('</div>', unsafe_allow_html=True)

            st.subheader("📈 Price Chart")
            st.line_chart(hist["Close"])

            payload = {
                "symbol": ticker,
                "as_of": datetime.utcnow().isoformat(),
                "technical": technicals,
                "fundamental": fundamentals,
            }

            result = ask_openai(payload)

            if "error" in result:
                st.error("OpenAI API Error:")
                st.code(result["error"])
            else:
                color_class = "buy" if result['action']=="BUY" else "hold" if result['action']=="HOLD" else "sell"
                st.markdown(f'<div class="recommendation {color_class}">{result["action"]} (Confidence: {result["confidence"]}%)</div>', unsafe_allow_html=True)
                st.markdown("### 🔹 Technical Summary")
                st.info(result["technical_summary"])
                st.markdown("### 🔹 Fundamental Summary")
                st.success(result["fundamental_summary"])
                if result.get("risks"):
                    st.markdown("### ⚠️ Risks")
                    st.warning("- " + "\n- ".join(result["risks"]))
                if result.get("notes"):
                    st.markdown("### 📝 Notes")
                    st.write(result["notes"])

st.divider()
st.caption("⚠️ For educational purposes only. Not financial advice.")
