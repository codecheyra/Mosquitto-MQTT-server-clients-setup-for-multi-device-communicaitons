import paho.mqtt.client as mqtt
import time
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

code_snippet_one = {
    "language": "python",
    "code": "print('Hello from Publisher One')"
}

while True:
    client.publish("topic/one", json.dumps(code_snippet_one))
    time.sleep(5)
