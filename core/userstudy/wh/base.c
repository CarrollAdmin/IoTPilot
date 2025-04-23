// Ready: DHT11 logic; DHTT headers;MQTT headers;; MQTT logic
// not ready:  0
// minimal code modification: 0%



#include <xtimer.h>
#include <stdio.h>
#include <stdlib.h>
#include <paho_mqtt.h>
#include <MQTTClient.h>
#include <net/sock/udp.h>
#include <dht.h>

#define DHT_PIN 17
#define MQTT_BROKER_IP "47.102.103.1" // Example IP, replace with actual broker IP
#define MQTT_BROKER_PORT 1883
#define PUBLISH_TOPIC "sensor/dht"
#define CLIENT_ID "riot_dht_client"

static dht_t dev;

void mqtt_publish(MQTTClient client, int16_t temp, int16_t hum) {
    char payload[256];
    MQTTMessage message;
    message.qos = QOS1;
    message.retained = 0;
    snprintf(payload, sizeof(payload), "Temperature: %d.%d°C, Humidity: %d.%d%% RH",
             temp / 10, temp % 10, hum / 10, hum % 10);
    message.payload = payload;
    message.payloadlen = strlen(payload);
    MQTTPublish(&client, PUBLISH_TOPIC, &message);
    printf("Published: %s\n", payload);
}

void connect_to_mqtt(MQTTClient *client) {
    Network network;
    MQTTPacket_connectData  options = MQTTPacket_connectData_initializer;
    // MQTTClientInit(client, &network, CLIENT_ID);

    NetworkInit(&network);
    NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
    options.clientID.cstring = (char *)CLIENT_ID;
    options.keepAliveInterval = 20;
    options.cleansession = 1;
    MQTTConnect(client, &options);
}

void read_dht_sensor(void) {
    int16_t temp, hum;
    dht_params_t params;
    params.pin = DHT_PIN;
    params.type = DHT11;

    // Initialize DHT sensor
    if (dht_init(&dev, &params) != DHT_OK) {
        printf("Error: unable to initialize DHT11\n");
        return;
    }

    // Create MQTT client
    MQTTClient client;
    connect_to_mqtt(&client);

    // Read loop
    while (1) {
        if (dht_read(&dev, &temp, &hum) != DHT_OK) {
            printf("Error: unable to read DHT11 data\n");
        } else {
            printf("Temperature: %d.%d°C, Humidity: %d.%d%% RH\n", temp / 10, temp % 10, hum / 10, hum % 10);
            mqtt_publish(client, temp, hum);
        }
        xtimer_sleep(30);
    }

    MQTTDisconnect(&client);
}

int main(void) {
    read_dht_sensor();
    return 0;
}
