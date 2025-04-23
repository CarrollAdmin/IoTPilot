// Ready: DHT11 logic; DHTT headers;MQTT logic
// not ready:  MQTT headers;; 
// minimal code modification: 5%


#include <unistd.h>
#include <paho_mqtt.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <stdatomic.h>
#include <arpa/inet.h>
#include <msg.h>
#include <thread.h>
#include <dht.h>
#include <dht_params.h>
#include <xtimer.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define MQTT_TOPIC "sensor/data"
#define DHT_PIN 4

static int mqtt_publish(MQTTClient *client, const char *topic, const char *payload) {
    MQTTMessage message;
    message.qos = QOS0;
    message.retained = 0;
    message.payload = (void *)payload;
    message.payloadlen = strlen(payload);
    return MQTTPublish(client, topic, &message);
}

int main(void) {
    Network network;
    MQTTClient client;
    unsigned char sendbuf[80], readbuf[80];
    int rc;

    NetworkInit(&network);
    rc = NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
    if (rc != SUCCESS) {
        printf("Failed to connect to network\n");
        return rc;
    }

    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    rc = MQTTConnect(&client, &connectData);
    if (rc != SUCCESS) {
        printf("Failed to connect to MQTT broker\n");
        return rc;
    }

    int16_t temperature, humidity;
    while (1) {
        if (dht_read(DHT_PIN, &temperature, &humidity) == DHT_OK) {
            char payload[50];
            snprintf(payload, sizeof(payload), "Temperature: %d, Humidity: %d", temperature, humidity);
            rc = mqtt_publish(&client, MQTT_TOPIC, payload);
            if (rc != SUCCESS) {
                printf("Failed to publish message\n");
            }
        } else {
            printf("Failed to read from DHT sensor\n");
        }
        sleep(5);
    }

    return 0;
}