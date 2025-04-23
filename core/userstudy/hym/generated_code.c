
// Ready: DHT11 logic; DHTT headers; MQTT logic; 1/2 MQTT headers
// not ready: 0
// minimal code modification: 0%

#include <stdio.h>
#include <msg.h>
#include <xtimer.h>
#include <dht.h>
#include <dht_params.h>
#include <net/emcute.h>
#include <MQTTClient.h>
#include <paho_mqtt.h>

#define MQTT_BROKER_IP "192.168.1.10"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/dht11"
#define DHT_PIN GPIO_PIN(0, 4)  // Example GPIO pin

static dht_t dht_dev;
static msg_t msg_queue[8];

void *mqtt_thread(void *arg) {
    (void)arg;
    MQTTClient client;
    Network network;
    unsigned char sendbuf[80], readbuf[80];
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;

    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));

    if (NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT) != SUCCESS) {
        printf("Failed to connect to network\n");
        return NULL;
    }

    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    if (MQTTConnect(&client, &connectData) != SUCCESS) {
        printf("Failed to connect to MQTT broker\n");
        return NULL;
    }

    while (1) {
        int16_t temperature, humidity;
        if (dht_read(&dht_dev, &temperature, &humidity) == DHT_OK) {
            char payload[50];
            snprintf(payload, sizeof(payload), "{\"temperature\": %d, \"humidity\": %d}", temperature, humidity);
            MQTTMessage message;
            message.qos = QOS0;
            message.retained = 0;
            message.payload = payload;
            message.payloadlen = strlen(payload);

            if (MQTTPublish(&client, MQTT_TOPIC, &message) != SUCCESS) {
                printf("Failed to publish message\n");
            }
        } else {
            printf("Failed to read from DHT11 sensor\n");
        }
        xtimer_sleep(10);
    }
    return NULL;
}

int main(void) {
    msg_init_queue(msg_queue, sizeof(msg_queue) / sizeof(msg_t));

    dht_params_t dht_params;
    dht_params.pin = DHT_PIN;
    dht_params.type = DHT11;

    if (dht_init(&dht_dev, &dht_params) != DHT_OK) {
        printf("Failed to initialize DHT11 sensor\n");
        return 1;
    }

    char stack[THREAD_STACKSIZE_MAIN];
    thread_create(stack, sizeof(stack), THREAD_PRIORITY_MAIN - 1, 0, mqtt_thread, NULL, "mqtt_thread");

    return 0;
}