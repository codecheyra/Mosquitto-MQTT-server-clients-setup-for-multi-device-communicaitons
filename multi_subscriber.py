import paho.mqtt.client as mqtt
import json

broker = "localhost"
port = 1883
topics = [f"topic/{i}" for i in range(1, 101)]  # List of 100 topics from topic/1 to topic/100

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for topic in topics:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    request = json.loads(msg.payload.decode())
    print(f"Request received on topic {msg.topic}: {request}")

    # Simulate REST API response if needed
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
