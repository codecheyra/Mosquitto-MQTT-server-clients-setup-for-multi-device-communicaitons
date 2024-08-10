import paho.mqtt.client as mqtt
import time
import json

client = mqtt.Client()
client.connect("localhost", 1883, 60)

code_snippet_two = {
    "language": "javascript",
    "code": "console.log('Hello from Publisher Two');"
}

while True:
    client.publish("topic/two", json.dumps(code_snippet_two))
    time.sleep(5)
