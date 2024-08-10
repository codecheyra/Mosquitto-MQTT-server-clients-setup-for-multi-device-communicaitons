import paho.mqtt.client as mqtt
import json

broker = "localhost"
port = 1883
topic = "api/request"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    request = json.loads(msg.payload.decode())
    print(f"Request received: {request}")

    # Simulate REST API response
    response_data = {
        "status": 200,
        "data": {"key": "value"}
    }

    response_topic = "api/response"
    client.publish(response_topic, json.dumps(response_data))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)

client.loop_forever()
