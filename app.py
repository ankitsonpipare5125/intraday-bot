import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime

st.set_page_config(page_title="Intraday Analyzer", layout="centered")
st.title("🚀 Intraday Trading Analyzer")
st.markdown("**Risk: 2.5% | Reward: 1:2**")

symbol = st.text_input("Enter Stock Symbol (NSE)", value="BANKNIFTY").upper().strip()

if st.button("🔍 Analyze Stock", type="primary"):
    with st.spinner(f"Fetching latest data for {symbol}..."):
        try:
            ticker = yf.Ticker(symbol + ".NS")
            df = ticker.history(period="5d", interval="5m")
            
            if len(df) < 30:
                st.error("Not enough data. Market may be closed.")
            else:
                df['EMA9'] = ta.ema(df['Close'], length=9)
                df['EMA21'] = ta.ema(df['Close'], length=21)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                st_df = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
                df = pd.concat([df, st_df], axis=1)
                df['VWAP'] = ta.vwap(df['High'], df['Low'], df['Close'], df['Volume'])

                latest = df.iloc[-1]
                price = round(latest['Close'], 2)

                ema_bull = latest['EMA9'] > latest['EMA21']
                rsi_ok = latest['RSI'] > 50
                super_ok = latest.get('SUPERTd_10_3.0', 0) > 0
                vwap_ok = price > latest['VWAP']

                if ema_bull and rsi_ok and super_ok and vwap_ok:
                    signal = "🟢 STRONG BUY"
                    color = "green"
                    sl = round(price * 0.975, 2)
                    target = round(price + 2*(price-sl), 2)
                elif not ema_bull and not rsi_ok and not super_ok:
                    signal = "🔴 STRONG SELL"
                    color = "red"
                    sl = round(price * 1.025, 2)
                    target = round(price - 2*(sl-price), 2)
                else:
                    signal = "⚪ NEUTRAL"
                    color = "orange"
                    sl = round(price * 0.975, 2)
                    target = round(price * 1.05, 2)

                st.success(f"**{symbol} — ₹{price}**")
                st.markdown(f"### Signal: <span style='color:{color}'>{signal}</span>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                col1.metric("Entry", f"₹{price}")
                col2.metric("Stop Loss", f"₹{sl}")
                col3.metric("Target", f"₹{target}")

                st.write("**Volume**:", f"{int(latest['Volume']):,}")

        except:
            st.error("Error! Check symbol or try after market opens.")

st.caption("Made for Ankit | Data from Yahoo Finance | Paper Trade Only")
