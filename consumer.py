# consumer.py
from kafka import KafkaConsumer
import json
import psycopg2

# PostgreSQL 연결 설정
conn = psycopg2.connect(
    dbname="bitcoin",
    user="admin",
    password="admin",
    host="localhost", # 이전 단계에서 수정됨
    port="5432"
)
conn.set_client_encoding('UTF8')
cursor = conn.cursor()

# --- 테이블 생성 로직 추가 ---
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS btc_trades (
        id SERIAL PRIMARY KEY,
        price NUMERIC,
        qty NUMERIC,
        timestamp BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit() # 테이블 생성 쿼리 실행 후 커밋
    print("Table 'btc_trades' checked/created successfully.")
except Exception as e:
    print(f"Error creating table: {e}")
    conn.rollback() # 오류 발생 시 롤백
    # 여기서 프로그램을 종료하거나 적절한 오류 처리를 할 수 있습니다.
# --- 여기까지 테이블 생성 로직 ---


# Kafka Consumer 설정
consumer = KafkaConsumer(
    'btc-trades',
    bootstrap_servers=['localhost:9092'], # Kafka 서버 주소 확인
    auto_offset_reset='earliest',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("대기중...")

for message in consumer:
    data = message.value
    price_str = data['p']  # 바이낸스에서 가격은 문자열로 옴
    qty_str = data['q']    # 바이낸스에서 수량은 문자열로 옴
    ts_bigint = data['T']  # 바이낸스 타임스탬프는 정수(밀리초)

    try:
        # 데이터베이스에 저장하기 전에 적절한 타입으로 변환 (필요시)
        # NUMERIC 타입은 문자열 형태의 숫자도 잘 받아들일 수 있음
        cursor.execute(
            "INSERT INTO btc_trades (price, qty, timestamp) VALUES (%s, %s, %s)",
            (price_str, qty_str, ts_bigint) # NUMERIC은 문자열 숫자도 잘 처리함
        )
        conn.commit()
        print(f"✅ 저장됨 - 가격: {price_str}, 수량: {qty_str}, 시간: {ts_bigint}")
    except Exception as e:
        print(f"Error inserting data: {e}")
        conn.rollback() # 개별 INSERT 실패 시 롤백

# 스크립트 종료 시 연결 닫기 (실제로는 무한 루프이므로 여기에 도달하지 않을 수 있음)
# cursor.close()
# conn.close()