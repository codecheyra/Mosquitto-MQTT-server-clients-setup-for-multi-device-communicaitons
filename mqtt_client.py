import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print(f"Python Client Connected with result code {rc}")
    client.subscribe("test/topic")
    client.subscribe("test/confirmation")

def on_message(client, userdata, msg):
    print(f"Python Client received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    if msg.topic == "test/confirmation":
        print("Python Client received confirmation from Broker")
        client.disconnect()
    else:
        client.publish("test/confirmation", f"Python Client received the message '{msg.payload.decode()}'")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()

client.publish("test/topic", "Hello from Python!")
print("Python Client: Sent message 'Hello from Python!' to topic 'test/topic'")
time.sleep(2)

client.loop_stop()
client.disconnect()
