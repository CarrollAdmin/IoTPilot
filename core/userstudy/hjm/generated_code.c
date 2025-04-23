// Ready: DHT11 logic; DHTT headers; MQTT logic; 1/2 MQTT headers
// not ready: 1/2 MQTT headers
// minimal code modification: 5%

#include <esp_system.h>
#include <esp_wifi.h>
#include <MQTTClient.h>
#include <msg.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <timex.h>
#include <unistd.h>
#include <ztimer.h>

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/dht11"
#define MQTT_CLIENT_ID "esp32_dht11"

static MQTTClient client;
static Network network;

void publish_sensor_data(int temperature, int humidity) {
    char payload[50];
    snprintf(payload, sizeof(payload), "Temperature: %d, Humidity: %d", temperature, humidity);
    MQTTMessage message;
    message.payload = payload;
    message.payloadlen = strlen(payload);
    message.qos = QOS0;
    message.retained = 0;
    MQTTPublish(&client, MQTT_TOPIC, &message);
}

int main(void) {
    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, NULL, 0, NULL, 0);
    NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
    MQTTConnect(&client, NULL);

    int temperature, humidity;
    while (1) {
        if (dht_read(NULL, &temperature, &humidity) == 0) {
            publish_sensor_data(temperature, humidity);
        }
        ztimer_sleep(ZTIMER_MSEC, 5000);
    }
    return 0;
}