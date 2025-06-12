import json
import time
import dotenv
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import asyncio
import threading
import paho.mqtt.client as mqtt
import os
dotenv.load_dotenv()

app = FastAPI()
latest_state = {}

# mqtt setup
MQTT_BROKER = os.getenv("BROKER_IP", "localhost")
MQTT_PORT = int(os.getenv("BROKER_PORT", 1883))
MQTT_USER = os.getenv("BROKER_USER", "")
MQTT_PASSWORD = os.getenv("BROKER_PASSWORD", "")
MQTT_TOPIC = os.getenv("BROKER_TOPIC", "test")

# store connected websocket clients
websocket_clients = set()

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_state
    payload = json.loads(msg.payload.decode())
    print(f"[MQTT] Message received on {msg.topic}: {payload}")
    latest_state = payload

    # notify all websocket clients
    for ws in websocket_clients:
        asyncio.run(send_to_websocket(ws, latest_state))

def mqtt_loop():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    if MQTT_USER and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()

# @app.on_event("startup")
def start_mqtt():
    thread = threading.Thread(target=mqtt_loop)
    thread.start()


@app.get("/")
def read_root():
    return {"message": "Factory Interface Running"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # can be used to trigger responses
    except:
        websocket_clients.remove(websocket)


async def send_to_websocket(websocket: WebSocket, data: dict):
    try:
        await websocket.send_json(data)
    except:
        websocket_clients.remove(websocket)


@app.get("/latest")
def get_latest_state():
    return latest_state

# Run the FastAPI app with:
# uvicorn fastApi:app --host

@app.on_event("startup")
def startup_event():
    start_mqtt()

