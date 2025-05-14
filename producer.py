import websocket, json
from kafka import KafkaProducer

# Kafka Producer 설정
producer = KafkaProducer(
    bootstrap_servers='localhost:9092', 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(ws, message):
    data = json.loads(message)
    price = data['p']
    quantity = data['q']
    print(f"체결가: {price}, 거래량: {quantity}")
    producer.send('btc-trades', data)

def on_open(ws):
    subscribe_msg = {
        "method": "SUBSCRIBE",
        "params": ["btcusdt@trade"],
        "id": 1
    }
    ws.send(json.dumps(subscribe_msg))

ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                            on_message=on_message,
                            on_open=on_open)
ws.run_forever()
