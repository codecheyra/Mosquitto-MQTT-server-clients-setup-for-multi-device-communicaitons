import paho.mqtt.client as mqtt
import json

broker = "localhost"
port = 1883
topic = "api/request"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect

client.connect(broker, port, 60)

request_data = {
    "method": "GET",
    "endpoint": "/data",
    "params": {}
}

client.loop_start()
client.publish(topic, json.dumps(request_data))
client.loop_stop()
client.disconnect()
