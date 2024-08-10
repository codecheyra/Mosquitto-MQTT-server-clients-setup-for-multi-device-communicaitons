# MQTT Client Communication via Broker

## Overview

This documentation describes how to set up and run MQTT clients (written in C, Python, and Java) communicating via a Mosquitto broker on multiple devices. The broker acts as an intermediary, facilitating message exchange between the clients. The communication setup and running process are detailed below.

## Index

- [Prerequisites](#prerequisites)
- [Setting Up the Broker](#setting-up-the-broker)
- [Client Implementations](#client-implementations)
  - [C Client](#c-client)
  - [Python Client](#python-client)
  - [Java Client](#java-client)
- [Running the Setup](#running-the-setup)

## Prerequisites

*Note: It is recommended to work in a Virtual environment.*

Ensure the following are installed on your Mac:

- Mosquitto (MQTT Broker)
- Paho MQTT library for C
- Python and Paho MQTT library for Python
- Java and Paho MQTT library for Java
- gcc compiler for C

### Install Required Software

**Install dependencies:**

```bash
brew install cmake git openssl

**Install C library:**

```bash
git clone https://github.com/eclipse/paho.mqtt.c.git
cd paho.mqtt.c  # Navigate to the paho.mqtt.c directory
mkdir build
cd build
cmake -DPAHO_WITH_SSL=ON -DPAHO_BUILD_STATIC=ON ..
make
sudo make install
```

**Install Python libraries:**

```bash
pip install Flask paho-mqtt
```

**Verify Java library existence:**

Ensure the `org.eclipse.paho.client.mqttv3-1.2.5.jar` file is present in your `lib` directory. If not, download it from [Eclipse Paho Downloads](https://www.eclipse.org/paho/downloads.php).

**Directory structure:**

```
project-folder/
├── ThreeMqttClient.java
└── lib/
    └── org.eclipse.paho.client.mqttv3-1.2.5.jar
```

## Setting Up the Broker

**Install Mosquitto:**

```bash
brew install mosquitto
```

**Edit Mosquitto Configuration:**

Create and edit the configuration file `/etc/mosquitto/mosquitto.conf`:

```bash
sudo mkdir -p /etc/mosquitto
sudo nano /etc/mosquitto/mosquitto.conf
```

Add the following lines:

```
listener 1883 0.0.0.0
allow_anonymous true
```

**Restart Mosquitto:**

Using Homebrew:

```bash
brew services restart mosquitto
```

Manually:

```bash
sudo killall mosquitto
mosquitto -c /etc/mosquitto/mosquitto.conf
```

## Broker Implementation

**File: `mqtt_broker.py`**

```python
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
```

**Run the Broker:**

```bash
python mqtt_broker.py
```

## Client Implementations

### C Client

**File: `mqtt_client.c`**

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "MQTTClient.h"

#define ADDRESS     "tcp://192.168.29.247:1883"  // Replace with IP of Machine A
#define CLIENTID    "ExampleClientPub"
#define TOPIC       "test/topic"
#define CONFIRMATION_TOPIC "test/confirmation"
#define PAYLOAD     "Hello from C!"
#define QOS         1
#define TIMEOUT     10000L

void onMessageDelivered(void *context, MQTTClient_deliveryToken dt) {
    printf("C Client: Message with token value %d delivery confirmed\n", dt);
}

void onConnectionLost(void *context, char *cause) {
    printf("C Client: Connection lost\n");
    printf("Cause: %s\n", cause);
}

int onMessageArrived(void *context, char *topicName, int topicLen, MQTTClient_message *message) {
    printf("C Client: Message arrived\n");
    printf("Topic: %s\n", topicName);
    printf("Message: %.*s\n", message->payloadlen, (char*)message->payload);
    if (strcmp(topicName, CONFIRMATION_TOPIC) == 0) {
        printf("C Client: Received confirmation from Broker\n");
        MQTTClient_disconnect((MQTTClient)context, 10000);
    } else {
        MQTTClient client = (MQTTClient)context;
        // Send confirmation back to broker
        MQTTClient_publish(client, CONFIRMATION_TOPIC, strlen("C Client received the message"), "C Client received the message", QOS, 0, NULL);
    }
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);
    return 1;
}

int main(int argc, char* argv[]) {
    MQTTClient client;
    MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
    int rc;

    MQTTClient_create(&client, ADDRESS, CLIENTID, MQTTCLIENT_PERSISTENCE_NONE, NULL);
    conn_opts.keepAliveInterval = 20;
    conn_opts.cleansession = 1;

    MQTTClient_setCallbacks(client, client, onConnectionLost, onMessageArrived, onMessageDelivered);

    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS) {
        printf("C Client: Failed to connect, return code %d\n", rc);
        exit(EXIT_FAILURE);
    }

    MQTTClient_subscribe(client, TOPIC, QOS);
    MQTTClient_subscribe(client, CONFIRMATION_TOPIC, QOS);

    MQTTClient_message pubmsg = MQTTClient_message_initializer;
    pubmsg.payload = PAYLOAD;
    pubmsg.payloadlen = strlen(PAYLOAD);
    pubmsg.qos = QOS;
    pubmsg.retained = 0;
    MQTTClient_deliveryToken token;

    MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token);
    printf("C Client: Sent message '%s' to topic '%s'\n", PAYLOAD, TOPIC);
    rc = MQTTClient_waitForCompletion(client, token, TIMEOUT);
    printf("C Client: Message with delivery token %d delivered\n", token);

    MQTTClient_disconnect(client, 10000);
    MQTTClient_destroy(&client);
    return rc;
}
```

**Compile the C Client:**

```bash
gcc mqtt_client.c -lpaho-mqtt3c -o mqtt_client
```

### Python Client

**File: `mqtt_client.py`**

```python
import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    print(f"Python Client: Connected with result code {rc}")
    client.subscribe("test/response_py")
    client.subscribe("test/confirmation")

def on_message(client, userdata, msg):
    print(f"Python Client received message '{msg.payload.decode()}' on topic '{msg.topic}'")
    if msg.topic == "test/confirmation":
        print("Python Client: Received confirmation from Broker")
    else:
        print(f"Python Client: Forwarding message '{msg.payload.decode()}' to Broker")
        client.publish("test/confirmation", f"Python Client received: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_start()

time.sleep(1)  # Ensure connection is established
print("Python Client: Sending message 'Hello from Python!' to topic 'test/topic'")
client.publish("test/topic", "Hello from Python!")

# Wait for a bit to receive messages
time.sleep(5)

client.loop_stop()
client.disconnect()
```

**Run the Python Client:**

```bash
python mqtt_client.py
```

### Java Client

**File: `ThreeMqttClient.java`**

```java
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;

public class ThreeMqttClient {

    private static final String BROKER_URL = "tcp://192.168.29.247:1883";  // Replace with IP of Machine A
    private static final String CLIENT_ID = "JavaClient";
    private static final String TOPIC = "test/topic";
    private static final String CONFIRMATION_TOPIC = "test/confirmation";
    private static final String PAYLOAD = "Hello from Java!";
    private static final int QOS = 1;

    public

 static void main(String[] args) {
        try {
            MqttClient client = new MqttClient(BROKER_URL, CLIENT_ID, new MemoryPersistence());
            MqttConnectOptions connOpts = new MqttConnectOptions();
            connOpts.setCleanSession(true);

            client.setCallback(new MqttCallback() {
                @Override
                public void connectionLost(Throwable cause) {
                    System.out.println("Java Client: Connection lost");
                }

                @Override
                public void messageArrived(String topic, MqttMessage message) throws Exception {
                    System.out.println("Java Client: Message arrived");
                    System.out.println("Topic: " + topic);
                    System.out.println("Message: " + new String(message.getPayload()));

                    if (topic.equals(CONFIRMATION_TOPIC)) {
                        System.out.println("Java Client: Received confirmation from Broker");
                        client.disconnect();
                    } else {
                        MqttMessage confirmMsg = new MqttMessage("Java Client received the message".getBytes());
                        client.publish(CONFIRMATION_TOPIC, confirmMsg);
                    }
                }

                @Override
                public void deliveryComplete(IMqttDeliveryToken token) {
                    System.out.println("Java Client: Delivery complete");
                }
            });

            client.connect(connOpts);
            client.subscribe(TOPIC);

            MqttMessage message = new MqttMessage(PAYLOAD.getBytes());
            message.setQos(QOS);

            client.publish(TOPIC, message);
            System.out.println("Java Client: Sent message 'Hello from Java!' to topic 'test/topic'");

        } catch (MqttException e) {
            e.printStackTrace();
        }
    }
}
```

**Compile and Run the Java Client:**

```bash
javac -cp .:/path/to/org.eclipse.paho.client.mqttv3-1.2.5.jar ThreeMqttClient.java
java -cp .:/path/to/org.eclipse.paho.client.mqttv3-1.2.5.jar ThreeMqttClient
```

Replace `/path/to/` with the actual path to your `org.eclipse.paho.client.mqttv3-1.2.5.jar` file.

**Example:**

```bash
javac -cp .:/Users/apple/Desktop/MQTT/lib/org.eclipse.paho.client.mqttv3_1.2.5.jar ThreeMqttClient.java
java -cp .:/Users/apple/Desktop/MQTT/lib/org.eclipse.paho.client.mqttv3_1.2.5.jar ThreeMqttClient
```

## Running the Setup

**Start the Broker:**

Ensure the broker is running with the updated configuration:

```bash
mosquitto -c /etc/mosquitto/mosquitto.conf
```

**Run the Clients in the following order:**

**C Client:**

```bash
gcc -o mqtt_client mqtt_client.c -lpaho-mqtt3c
./mqtt_client
```

**Python Client:**

```bash
python mqtt_client.py
```

**Java Client:**

```bash
javac -cp .:/path/to/org.eclipse.paho.client.mqttv3-1.2.5.jar ThreeMqttClient.java
java -cp .:/path/to/org.eclipse.paho.client.mqttv3-1.2.5.jar ThreeMqttClient
```

Ensure that the broker IP (`<BROKER_IP>`) is replaced with the actual IP address of the machine where the broker is running.

The setup is such that the broker is running on Machine A and clients like Python and Java are running on Machine B. Communications should pass successfully.
