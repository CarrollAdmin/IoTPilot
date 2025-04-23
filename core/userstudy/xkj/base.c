// Ready: DHT11 logic; DHTT headers;MQTT headers;; MQTT logic
// not ready:  0
// minimal code modification: 0%




#include <string.h>
#include <stdio.h>
#include <stdint.h>
#include "net/sock/util.h"
#include "net/sock/udp.h"
#include "dht.h"
#include "MQTTClient.h"
#include "paho_mqtt.h"

#define BROKER_IP "47.102.103.1"
#define BROKER_PORT 1883
#define DHT_PIN GPIO_PIN(0, 0) // Assuming port is 0
#define DHT_TYPE DHT11

static dht_t dht_dev;

void publish_data(MQTTClient* client, float temperature, float humidity) {
    // Prepare the MQTT message payload
    char payload[50];
    snprintf(payload, sizeof(payload), "Temperature: %.1f, Humidity: %.1f", temperature, humidity);
    
    // Create a new MQTT message
    MQTTMessage message;
    message.qos = QOS0;
    message.retained = 0;
    message.dup = 0;
    message.payload = payload;
    message.payloadlen = strlen(payload);

    // Publish the message
    MQTTPublish(client, "sensors/dht", &message);
}

int main(void) {
    int16_t temperature, humidity;
    Network network;

    // Initialize network
    NetworkInit(&network);
    if (NetworkConnect(&network, BROKER_IP, BROKER_PORT) != 0) {
        printf("Failed to connect to network\n");
        return -1;
    }

    // Initialize MQTT Client
    unsigned char sendbuf[80], readbuf[80];
    MQTTClient client;
    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "dhtSensorClient";
    
    // Connect to MQTT broker
    if (MQTTConnect(&client, &connectData) != SUCCESS) {
        printf("Failed to connect to broker\n");
        return -1;
    }

    // Initialize DHT sensor
    if (dht_init(&dht_dev, &DHT_TYPE) != DHT_OK) {
        printf("Failed to initialize DHT sensor\n");
        return -1;
    }

    // Read data from DHT sensor
    if (dht_read(&dht_dev, &temperature, &humidity) != DHT_OK) {
        printf("Failed to read from DHT sensor\n");
        return -1;
    }

    float temp_c = temperature / 10.0;
    float hum = humidity / 10.0;

    // Publish data
    publish_data(&client, temp_c, hum);

    // Disconnect from the MQTT broker
    MQTTDisconnect(&client);
    NetworkDisconnect(&network);

    return 0;
}