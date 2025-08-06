import asyncio
import json
import websockets
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


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
                payload = {"price": data["p"], "timestamp": data["T"]}
                await producer.send_and_wait(TOPIC, json.dumps(payload).encode("utf-8"))
            except Exception as e:
                print("Error handling message:", e)


@app.on_event("startup")
async def startup_event():
    await start_kafka_producer()
    asyncio.create_task(consume_binance_ws())
    global consumer
    consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="my-group",
        auto_offset_reset="latest",
        value_deserializer=lambda m: m.decode("utf-8"),
    )
    await consumer.start()


@app.on_event("shutdown")
async def shutdown_event():
    await stop_kafka_producer()
    await consumer.stop()


@app.get("/consume")
async def consume_message():
    try:
        msg = await consumer.getone()
    except Exception:
        return {"message": "No messages available"}
    if msg:
        try:
            return json.loads(msg.value)
        except json.JSONDecodeError:
            return {"message": msg.value}


@app.websocket("/ws/kafka")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            msg = await consumer.getone()
            try:
                data = json.loads(msg.value)
            except json.JSONDecodeError:
                data = {"message": msg.value}
            await websocket.send_json(data)
    except WebSocketDisconnect:
        print("Client déconnecté")
    except Exception as e:
        print(f"Erreur dans WebSocket: {e}")
