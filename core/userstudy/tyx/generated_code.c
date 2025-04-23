
// Ready: DHT11 logic; DHTT headers; MQTT logic; 1/2 MQTT headers
// not ready: 0
// minimal code modification: 0%


#include <unistd.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#include "paho_mqtt.h"
#include "esp_wifi.h"
#include "thread.h"
#include "MQTTClient.h"
#include "dht.h"
#include "dht_params.h"
#include "time_units.h"
#include "event/thread.h"

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define DHT_PIN 4

static MQTTClient client;
static Network network;

void publish_sensor_data(void) {
    int16_t temperature, humidity;
    dht_t dev;
    dht_params_t params = {
        .pin = DHT_PIN,
        .type = DHT11
    };

    if (dht_init(&dev, &params) != DHT_OK) {
        printf("Failed to initialize DHT11\n");
        return;
    }

    if (dht_read(&dev, &temperature, &humidity) != DHT_OK) {
        printf("Failed to read from DHT11\n");
        return;
    }

    char payload[50];
    snprintf(payload, sizeof(payload), "Temperature: %d.%d C, Humidity: %d.%d %%", temperature / 10, temperature % 10, humidity / 10, humidity % 10);

    MQTTMessage message;
    message.qos = QOS0;
    message.retained = 0;
    message.payload = payload;
    message.payloadlen = strlen(payload);

    if (MQTTPublish(&client, "sensor/data", &message) != SUCCESS) {
        printf("Failed to publish message\n");
    }
}

void *mqtt_thread(void *arg) {
    (void)arg;
    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, NULL, 0, NULL, 0);

    if (NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT) != 0) {
        printf("Failed to connect to network\n");
        return NULL;
    }

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    if (MQTTConnect(&client, &connectData) != SUCCESS) {
        printf("Failed to connect to MQTT broker\n");
        return NULL;
    }

    while (1) {
        publish_sensor_data();
        ztimer_sleep(ZTIMER_MSEC, 5000);
    }

    return NULL;
}

int main(void) {
    char stack[THREAD_STACKSIZE_MAIN];
    thread_create(stack, sizeof(stack), THREAD_PRIORITY_MAIN - 1, 0, mqtt_thread, NULL, "mqtt_thread");
    return 0;
}