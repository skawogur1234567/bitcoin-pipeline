import streamlit as st
import websocket
import threading
import json
from collections import deque
import pandas as pd
import plotly.express as px
import time


# 최대 저장할 데이터 수
MAX_POINTS = 50
prices = deque(maxlen=MAX_POINTS)
times = deque(maxlen=MAX_POINTS)

# 웹소켓 콜백
def on_message(ws, message):
    data = json.loads(message)
    prices.append(float(data['p']))
    times.append(pd.Timestamp.now().strftime('%H:%M:%S'))

def on_open(ws):
    subscribe_msg = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": 1
    }
    ws.send(json.dumps(subscribe_msg))

# 웹소켓을 백그라운드에서 실행
def start_ws():
    ws = websocket.WebSocketApp(
        "wss://stream.binance.com:9443/ws/btcusdt@trade",
        on_message=on_message,
        on_open=on_open
    )
    ws.run_forever()

# Websocket thread 시작 (앱 실행시 최초 1번만)
if "started" not in st.session_state:
    threading.Thread(target=start_ws, daemon=True).start()
    st.session_state.started = True

# Streamlit UI
st.title("💹 실시간 BTC/USDT ")

chart_area = st.empty()

while True:
    if prices and times:
        df = pd.DataFrame({"시간": list(times), "가격": list(prices)})
        fig = px.line(df, x="시간", y="가격", title="BTC/USDT 실시간 가격", markers=True)
        chart_area.plotly_chart(fig, use_container_width=True)
    time.sleep(1)