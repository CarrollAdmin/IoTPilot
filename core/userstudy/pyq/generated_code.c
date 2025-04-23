// Ready: DHT11 logic;1/2 MQTT headers; MQTT logic
// not ready: 1/2 MQTT headers;; DHTT headers
// minimal code modification: 10%


#include <stdio.h>
#include <stdlib.h>
#include <thread.h>
#include <unistd.h>
#include <ztimer.h>
#include <paho_mqtt.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <stddef.h>
#include <arpa/inet.h>
#include <esp_wifi.h>

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/dht11"

static dht_t dht_dev;
static Network network;
static MQTTClient client;

void mqtt_publish(float temperature, float humidity) {
    char payload[50];
    snprintf(payload, sizeof(payload), "{\"temperature\": %.2f, \"humidity\": %.2f}", temperature, humidity);
    MQTTPublish(&client, MQTT_TOPIC, payload);
}

int main(void) {
    // Initialize network
    NetworkInit(&network);
    NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);

    // Initialize MQTT client
    unsigned char sendbuf[100], readbuf[100];
    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));
    MQTTConnect(&client, NULL);

    // Initialize DHT11 sensor
    dht_params_t params;
    params.pin = GPIO_PIN(0, 4); // Example GPIO pin
    dht_init(&dht_dev, &params);

    while (1) {
        int16_t temperature, humidity;
        if (dht_read(&dht_dev, &temperature, &humidity) == 0) {
            mqtt_publish(temperature / 10.0, humidity / 10.0);
        }
        ztimer_sleep(ZTIMER_MSEC, 5000); // Sleep for 5 seconds
    }

    // Disconnect MQTT
    MQTTDisconnect(&client);
    NetworkDisconnect(&network);

    return 0;
}