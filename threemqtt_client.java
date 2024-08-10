import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;

public class threemqtt_client {
    private static final String BROKER_URL = "tcp://192.168.29.210:1883";
    private static final String CLIENT_ID = "JavaClient";
    private static final String TOPIC = "test/topic";
    private static final String CONFIRMATION_TOPIC = "test/confirmation";

    public static void main(String[] args) throws MqttException {
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
                    // Send confirmation back to broker
                    client.publish(CONFIRMATION_TOPIC, new MqttMessage("Java Client received the message".getBytes()));
                }
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                System.out.println("Java Client: Message with token value " + token + " delivery confirmed");
            }
        });

        client.connect(connOpts);

        // Subscribe to the topic
        client.subscribe(TOPIC);
        client.subscribe(CONFIRMATION_TOPIC);

        // Publish a message to the topic
        MqttMessage message = new MqttMessage("Hello from Java!".getBytes());
        message.setQos(1);
        client.publish(TOPIC, message);
        System.out.println("Java Client: Sent message 'Hello from Java!' to topic 'test/topic'");
    }
}
