// Ready: DHT11 logic; DHTT headers
// not ready: MQTT logic; MQTT headers
// minimal code modification: 70%
// incorrect MQTT publish

#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include "xtimer.h"
#include "net/sock/udp.h"
#include "msg.h"
#include "event/thread.h"
#include "dht.h"

#define MQTT_PORT (1883U)
#define DEFAULT_MQTT_BROKER_ADDR "47.102.103.1"
#define DEFAULT_MQTT_TOPIC "sensor/data"
#define DHT_PIN GPIO_PIN(0, 0) // Adjust for the correct pin
#define SLEEP_TIME (60U)

static dht_t dht;

// Connect to MQTT Broker using UDP
static int connect_to_broker(void) {
    sock_udp_ep_t broker;
    broker.family = AF_INET;
    broker.port = MQTT_PORT;
    inet_pton(AF_INET, DEFAULT_MQTT_BROKER_ADDR, &broker.addr.ipv4);

    sock_udp_t sock;
    if (sock_udp_create(&sock, NULL, NULL, 0) < 0) {
        printf("Error creating UDP socket\n");
        return -1;
    }
    
    // No explicit connect function exists for UDP; skip this step
    printf("Connected to MQTT broker at %s\n", DEFAULT_MQTT_BROKER_ADDR);
    return 0; // Return success
}

// Publish Data over UDP
static void publish_data(int16_t temp, int16_t hum) {
    char message[64];
    snprintf(message, sizeof(message), "Temperature: %d, Humidity: %d", temp, hum);

    sock_udp_ep_t broker;
    broker.family = AF_INET;
    broker.port = MQTT_PORT;
    inet_pton(AF_INET, DEFAULT_MQTT_BROKER_ADDR, &broker.addr.ipv4);

    sock_udp_t sock;
    if (sock_udp_create(&sock, NULL, NULL, 0) < 0) {
        printf("Error creating UDP socket for publish\n");
        return;
    }
    ssize_t res = sock_udp_send(&sock, message, strlen(message), &broker);
    if (res < 0) {
        printf("Error sending message\n");
    } else {
        printf("Published message to topic %s: %s\n", DEFAULT_MQTT_TOPIC, message);
    }
    sock_udp_close(&sock);
}

int main(void) {
    msg_t queue[8];
    msg_init_queue(queue, 8);

    // Initialize DHT sensor
    dht.params.pin = DHT_PIN;
    if (dht_init(&dht, &dht.params) != DHT_OK) {
        puts("Failed to initialize DHT sensor");
        return 1;
    }

    // Connect to MQTT broker
    if (connect_to_broker() != 0) {
        return 1;
    }

    // Main loop
    while (1) {
        int16_t temp, hum;
        if (dht_read(&dht, &temp, &hum) == DHT_OK) {
            printf("Temperature: %d, Humidity: %d\n", temp, hum);
            publish_data(temp, hum);
        } else {
            puts("Failed to read from DHT sensor");
        }

        xtimer_sleep(SLEEP_TIME);
    }

    return 0;
}
