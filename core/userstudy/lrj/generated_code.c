// Ready: DHT11 logic; DHTT headers;1/2 MQTT headers; MQTT logic
// not ready: 1/2 MQTT headers;
// minimal code modification: 5%


#include <arpa/inet.h>
#include <msg.h>
#include <paho_mqtt.h>
#include <stdio.h>
#include <stdlib.h>
#include <thread.h>
#include <unistd.h>

#include "dht.h"
#include "dht_params.h"
#include "MQTTClient.h"

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/data"
#define DHT_PIN GPIO_PIN(0, 4)  // Example GPIO pin

static char stack[THREAD_STACKSIZE_MAIN];

void *mqtt_thread(void *arg) {
    (void)arg;
    MQTTClient client;
    Network network;
    unsigned char sendbuf[80], readbuf[80];
    int rc;

    NetworkInit(&network);
    rc = NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
    if (rc != SUCCESS) {
        printf("Failed to connect to network\n");
        return NULL;
    }

    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    rc = MQTTConnect(&client, &connectData);
    if (rc != SUCCESS) {
        printf("Failed to connect to MQTT broker\n");
        return NULL;
    }

    dht_t dev;
    dht_params_t params = {
        .pin = DHT_PIN,
        .type = DHT11
    };
    dht_init(&dev, &params);

    while (1) {
        int16_t temp, hum;
        if (dht_read(&dev, &temp, &hum) == DHT_OK) {
            char payload[50];
            snprintf(payload, sizeof(payload), "{\"temperature\": %d, \"humidity\": %d}", temp, hum);
            MQTTMessage message;
            message.qos = QOS0;
            message.retained = 0;
            message.payload = payload;
            message.payloadlen = strlen(payload);

            rc = MQTTPublish(&client, MQTT_TOPIC, &message);
            if (rc != SUCCESS) {
                printf("Failed to publish message\n");
            }
        }
        sleep(5);
    }

    return NULL;
}

int main(void) {
    thread_create(stack, sizeof(stack), THREAD_PRIORITY_MAIN - 1, 0, mqtt_thread, NULL, "mqtt_thread");
    return 0;
}