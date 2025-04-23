// Ready: DHT11 logic;1/2 MQTT headers; MQTT logic;; DHTT headers
// not ready: 1/2 MQTT headers
// minimal code modification: 5%

#include <MQTTClient.h>
#include <esp_wifi.h>
#include <esp_system.h>
#include <msg.h>
#include <evtimer_msg.h>
#include <dht_params.h>
#include <dht.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/data"
#define DHT_PIN 4
#define MQTT_CLIENT_ID "esp32_client"
#define MQTT_USER NULL
#define MQTT_PASS NULL

static MQTTClient client;
static Network network;

void read_dht_and_publish(void) {
    int16_t temperature, humidity;
    if (dht_read(DHT_PIN, &temperature, &humidity) == 0) {
        char payload[50];
        snprintf(payload, sizeof(payload), "Temperature: %d.%d C, Humidity: %d.%d %%", temperature / 10, temperature % 10, humidity / 10, humidity % 10);
        MQTTMessage message;
        message.qos = QOS0;
        message.retained = 0;
        message.payload = payload;
        message.payloadlen = strlen(payload);
        MQTTPublish(&client, MQTT_TOPIC, &message);
    } else {
        printf("Failed to read from DHT sensor\n");
    }
}

int main(void) {
    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, NULL, 0, NULL, 0);

    if (NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT) != 0) {
        printf("Failed to connect to network\n");
        return -1;
    }

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = MQTT_CLIENT_ID;
    connectData.username.cstring = MQTT_USER;
    connectData.password.cstring = MQTT_PASS;

    if (MQTTConnect(&client, &connectData) != 0) {
        printf("Failed to connect to MQTT broker\n");
        return -1;
    }

    while (1) {
        read_dht_and_publish();
        sleep(10);  // Publish every 10 seconds
    }

    return 0;
}