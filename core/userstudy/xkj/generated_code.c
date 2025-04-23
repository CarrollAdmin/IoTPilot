
// Ready: DHT11 logic; DHTT headers; MQTT logic; 1/2 MQTT headers
// not ready: 0
// minimal code modification: 0%


#include <thread.h>
#include <paho_mqtt.h>
#include <dht_params.h>
#include <event/thread.h>
#include <MQTTClient.h>
#include <dht.h>

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/dht11"

static dht_t dht_dev;
static MQTTClient client;
static Network network;

void *mqtt_thread(void *arg) {
    (void)arg;
    int16_t temperature, humidity;
    char payload[64];

    NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
    MQTTClientInit(&client, &network, 1000, NULL, 0, NULL, 0);
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    if (MQTTConnect(&client, &connectData) != SUCCESS) {
        printf("Failed to connect to MQTT broker\n");
        return NULL;
    }

    while (1) {
        if (dht_read(&dht_dev, &temperature, &humidity) == DHT_OK) {
            snprintf(payload, sizeof(payload), "{\"temperature\": %d, \"humidity\": %d}", temperature, humidity);
            MQTTMessage message;
            message.qos = QOS0;
            message.retained = 0;
            message.payload = payload;
            message.payloadlen = strlen(payload);

            if (MQTTPublish(&client, MQTT_TOPIC, &message) != SUCCESS) {
                printf("Failed to publish message\n");
            }
        }
        thread_sleep();
    }
    return NULL;
}

int main(void) {
    dht_params_t dht_params = DHT_PARAMS;
    dht_init(&dht_dev, &dht_params);

    char stack[THREAD_STACKSIZE_MAIN];
    thread_create(stack, sizeof(stack), THREAD_PRIORITY_MAIN - 1, 0, mqtt_thread, NULL, "mqtt_thread");

    return 0;
}