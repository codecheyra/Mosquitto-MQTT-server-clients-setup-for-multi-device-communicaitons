import paho.mqtt.client as mqtt
import time
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

code_snippet = {
    "language": "python",
    "code": "print('Hello, World!')"
}

while True:
    client.publish("test/topic", json.dumps(code_snippet))
    time.sleep(5)
