// Ready: DHT11 logic; DHTT headers;
// not ready:  MQTT headers;; MQTT logic
// minimal code modification: 70%
// incorrect MQTT publish


#include <xtimer.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <net/sock/udp.h>  // For UDP socket
#include <net/af.h>        // For AF_INET
#include <arpa/inet.h>     // For inet_pton
#include <dht.h>

#define DHT_PIN 17
#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define PUBLISH_TOPIC "sensor/dht"
#define CLIENT_ID "riot_dht_client"

dht_t dev;

void mqtt_publish_temp_hum(int16_t temp, int16_t hum) {
    // Create the socket
    sock_udp_t sock;
    sock_udp_ep_t remote;

    // Construct the MQTT message: CONNECT, PUBLISH
    char message[256];
    snprintf(message, sizeof(message),
             "Temperature: %d.%d°C, Humidity: %d.%d%% RH",
             temp / 10, temp % 10, hum / 10, hum % 10);

    remote.family = AF_INET;
    remote.port = MQTT_BROKER_PORT;
    inet_pton(AF_INET, MQTT_BROKER_IP, &remote.addr);

    if (sock_udp_create(&sock, NULL, NULL, 0) < 0) {
        puts("Error: Unable to create UDP socket\n");
        return;
    }

    // Connect message
    char connect_msg[] = "MQTT Connect Message";  // Define as per the MQTT spec
    if (sock_udp_send(&sock, connect_msg, strlen(connect_msg), &remote) < 0) {
        puts("Error: Unable to send MQTT connect message\n");
        sock_udp_close(&sock);
        return;
    }

    // Publish message
    if (sock_udp_send(&sock, message, strlen(message), &remote) < 0) {
        puts("Error: Unable to publish MQTT message\n");
    }

    // Disconnect the MQTT session: DISCONNECT (if needed as per spec)
    char disconnect_msg[] = "MQTT Disconnect Message";  // Define as per the MQTT spec
    if (sock_udp_send(&sock, disconnect_msg, strlen(disconnect_msg), &remote) < 0) {
        puts("Error: Unable to send MQTT disconnect message\n");
    }

    sock_udp_close(&sock);
}

void read_dht_sensor(void) {
    int16_t temp, hum;
    dht_params_t params = { .pin = DHT_PIN, .type = DHT11 };

    if (dht_init(&dev, &params) != DHT_OK) {
        printf("Error: unable to initialize DHT11\n");
        return;
    }

    while (1) {
        if (dht_read(&dev, &temp, &hum) != DHT_OK) {
            printf("Error: unable to read DHT11 data\n");
        } else {
            printf("Temperature: %d.%d°C, Humidity: %d.%d%% RH\n", temp / 10, temp % 10, hum / 10, hum % 10);
            mqtt_publish_temp_hum(temp, hum);
        }
        xtimer_sleep(30);
    }
}

int main(void) {
    read_dht_sensor();
    return 0;
}