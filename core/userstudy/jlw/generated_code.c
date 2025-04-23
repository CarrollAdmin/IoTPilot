// Ready: DHT11 logic; DHTT headers;MQTT logic;1/2 MQTT headers
// not ready: 1/2 MQTT headers
// minimal code modification: 5%


#include <unistd.h>
#include <paho_mqtt.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <msg.h>
#include <arpa/inet.h>
#include <thread.h>
#include <dht.h>
#include <xtimer.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdbool.h>

#define CLOUD_IP "47.102.103.1"
#define CLOUD_PORT 1883

typedef struct Timer {
    unsigned int end_time;
} Timer;

typedef struct Network {
    int socket;
} Network;

void TimerInit(Timer* timer) {
    timer->end_time = 0;
}

void NetworkInit(Network* network) {
    network->socket = -1;
}

int main(void) {
    MQTTClient client;
    Network network;
    Timer timer;
    unsigned char sendbuf[100], readbuf[100];

    TimerInit(&timer);
    NetworkInit(&network);

    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));

    if (NetworkConnect(&network, CLOUD_IP, CLOUD_PORT) != 0) {
        printf("Failed to connect to network\n");
        return -1;
    }

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "ESP32Client";

    if (MQTTConnect(&client, &connectData) != 0) {
        printf("Failed to connect to MQTT broker\n");
        return -1;
    }

    int16_t temperature, humidity;
    dht_read(NULL, &temperature, &humidity);

    char payload[50];
    snprintf(payload, sizeof(payload), "Temperature: %d, Humidity: %d", temperature, humidity);

    MQTTMessage message;
    message.payload = payload;
    message.payloadlen = strlen(payload);
    message.qos = QOS0;
    message.retained = 0;

    if (MQTTPublish(&client, "sensor/data", &message) != 0) {
        printf("Failed to publish message\n");
        return -1;
    }

    printf("Message published successfully\n");
    return 0;
}