import asyncio
import json
import websockets
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "binance-trades"
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

app = FastAPI()

producer = None


async def start_kafka_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    print("Kafka producer started")


async def stop_kafka_producer():
    if producer:
        await producer.stop()
        print("Kafka producer stopped")


async def consume_binance_ws():
    async with websockets.connect(BINANCE_WS_URL) as websocket:
        print("Connected to Binance WebSocket")
        async for message in websocket:
            try:
                data = json.loads(message)
                print("Received message from Binance:", data)
                payload = {"price": data["p"], "timestamp": data["T"]}
                await producer.send_and_wait(TOPIC, json.dumps(payload).encode("utf-8"))
                print("Message sent to Kafka:", payload)
            except Exception as e:
                print("Error handling message:", e)


@app.on_event("startup")
async def startup_event():
    await start_kafka_producer()
    asyncio.create_task(consume_binance_ws())


@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka_producer()


@app.get("/")
def root():
    return {"status": "provider running"}
