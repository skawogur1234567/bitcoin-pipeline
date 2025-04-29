from kafka import KafkaConsumer
import json
import psycopg2

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    dbname="bitcoin", 
    user="admin", 
    password="admin", 
    host="postgres", 
    port="5432"
)
conn.set_client_encoding('UTF8')
cursor = conn.cursor()

# Kafka Consumer 설정
consumer = KafkaConsumer(
    'btc-trades',
    bootstrap_servers=['kafka:9092'],  
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("대기중...")

for message in consumer:
    data = message.value
    price = data['p']
    qty = data['q']
    ts = data['T']

    cursor.execute(
        "INSERT INTO btc_trades (price, qty, timestamp) VALUES (%s, %s, %s)",
        (price, qty, ts)
    )
    conn.commit()

    print(f"✅ 저장됨 - 가격: {price}, 수량: {qty}, 시간: {ts}")
