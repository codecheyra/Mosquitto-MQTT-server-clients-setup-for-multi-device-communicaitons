import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Broker: Connected with result code {rc}")
    client.subscribe("test/topic")
    client.subscribe("test/confirmation")

def on_message(client, userdata, msg):
    print(f"Broker: Received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    if msg.topic == "test/confirmation":
        print(f"Broker: Received confirmation '{msg.payload.decode()}' from client")
    elif msg.topic == "test/topic":
        print(f"Broker: Forwarding message '{msg.payload.decode()}' to clients")
        client.publish("test/confirmation", f"Broker received: {msg.payload.decode()}")
        client.publish("test/response_py", msg.payload.decode())
        client.publish("test/response_c", msg.payload.decode())
        client.publish("test/response_java", msg.payload.decode())

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()