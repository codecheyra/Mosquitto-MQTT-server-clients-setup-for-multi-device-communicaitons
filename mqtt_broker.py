# mqtt_broker.py
from flask import Flask
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''  # Set this if your broker requires authentication
app.config['MQTT_PASSWORD'] = ''  # Set this if your broker requires authentication
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False

mqtt = Mqtt(app)

@app.route('/')
def index():
    return "MQTT Broker is running!"

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('test/topic')
    print("Connected to MQTT Broker")

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    print(f"Message received: Topic: {message.topic}, Message: {message.payload.decode()}")
    if message.payload.decode() == 'Hello from C':
        mqtt.publish('test/response', 'Hello from Broker, forwarding to Python')
    elif message.payload.decode() == 'Hello from Python':
        mqtt.publish('test/response', 'Hello from Broker, forwarding to C')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
