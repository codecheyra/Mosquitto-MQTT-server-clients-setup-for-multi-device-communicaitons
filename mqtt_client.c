#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "MQTTClient.h"

#define ADDRESS     "tcp://localhost:1883"
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
