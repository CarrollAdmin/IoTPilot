// Ready: DHT11 logic; DHTT headers; MQTT logic
// not ready:  MQTT headers;;
// minimal code modification: 5%


#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <net/sock/udp.h>  // Corrected path to include udp.h
#include <dht.h>
#include <arpa/inet.h>  // Added header for inet_pton
#include <xtimer.h>
#include <paho_mqtt.h>  // Paho MQTT library
#include <sys/types.h> // For Timer, Mutex, Network etc.

#define DHT_PIN 17
#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define PUBLISH_TOPIC "sensor/dht"
#define CLIENT_ID "riot_dht_client"

// Define the necessary structures if not already defined
struct Network {
    sock_udp_t sock;
    int (*mqttread) (struct Network*, unsigned char*, int, int);
    int (*mqttwrite) (struct Network*, unsigned char*, int, int);
};

// Declare the network globally if needed
struct Network network;

dht_t dev;

void mqtt_publish(MQTTClient *client, int16_t temp, int16_t hum) {
    char payload[256];
    MQTTMessage message = {0};
    message.qos = 1;
    message.retained = 0;
    snprintf(payload, sizeof(payload), "Temperature: %d.%d°C, Humidity: %d.%d%% RH",
             temp / 10, temp % 10, hum / 10, hum % 10);
    message.payload = payload;
    message.payloadlen = strlen(payload);
    MQTTPublish(client, PUBLISH_TOPIC, &message);
    printf("Published: %s\n", payload);
}

void connect_to_mqtt(MQTTClient *client) {
    // Use the correct method or initialize structure properly
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    MQTTClientInit(client, &network, 1000, NULL, 0, NULL, 0);

    // network struct initialization
    sock_udp_ep_t remote = { .family = AF_INET, .port = MQTT_BROKER_PORT };
    inet_pton(AF_INET, MQTT_BROKER_IP, &remote.addr.ipv4);
    sock_udp_create(&network.sock, NULL, &remote, 0);

    connectData.keepAliveInterval = 20;
    connectData.cleansession = 1;
    MQTTConnect(client, &connectData);
}

void read_dht_sensor(void) {
    int16_t temp, hum;
    dht_params_t params = { .pin = DHT_PIN, .type = DHT11 };

    if (dht_init(&dev, &params) != DHT_OK) {
        printf("Error: unable to initialize DHT11\n");
        return;
    }

    MQTTClient client;
    connect_to_mqtt(&client);

    while (1) {
        if (dht_read(&dev, &temp, &hum) != DHT_OK) {
            printf("Error: unable to read DHT11 data\n");
        } else {
            printf("Temperature: %d.%d°C, Humidity: %d.%d%% RH\n", temp / 10, temp % 10, hum / 10, hum % 10);
            mqtt_publish(&client, temp, hum);
        }
        xtimer_sleep(30);
    }

    MQTTDisconnect(&client);
}

int main(void) {
    read_dht_sensor();
    return 0;
}
