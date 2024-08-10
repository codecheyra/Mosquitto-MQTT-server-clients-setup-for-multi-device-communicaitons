import paho.mqtt.client as mqtt
import json

broker = "localhost"
port = 1883
topic = "topic/two"  # Different topic for a different subscriber

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    request = json.loads(msg.payload.decode())
    print(f"Request received on topic {msg.topic}: {request}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker, port, 60)
client.loop_forever()
