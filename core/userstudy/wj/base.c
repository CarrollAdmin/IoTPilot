// Ready: DHT11 logic; DHTT headers;
// not ready:  MQTT headers;; MQTT logic
// minimal code modification: 60%


#include <string.h>
#include <stdio.h>
#include "xtimer.h"
#include "dht.h"
#include "msg.h"
#include "net/sock/udp.h"

#define SENSOR_PIN          GPIO_PIN(0, 10)  // Assuming port 0 for corrections
#define DHT_TYPE            DHT11

#define EMCUTE_ID           "gertrud"
#define SERVER_ADDRESS      "47.102.103.1"
#define SERVER_PORT         1883

mqttsn_con_t mqtt_conf;

dht_t dev;

static void read_and_publish(void) {
    // Initialize temperature and humidity variables
    int16_t temperature, humidity;
    
    if (dht_read(&dev, &temperature, &humidity) != DHT_OK) {
        printf("Failed to read DHT sensor\n");
        return;
    }
    
    printf("Temperature: %d.%d°C, Humidity: %d.%d%%\n", 
           temperature / 10, temperature % 10,
           humidity / 10, humidity % 10);

    // Prepare MQTT-SN message (since regular MQTT is not used)
    char message[64];
    snprintf(message, sizeof(message), "{\"temperature\": %d.%d, \"humidity\": %d.%d}",
             temperature / 10, temperature % 10,
             humidity / 10, humidity % 10);

    // Publish message
    mqttsn_pub(&mqtt_conf, "sensor/data", message, strlen(message));
    printf("Published data to MQTT broker\n");
}

int main(void) {
    // Initialize DHT sensor
    if (dht_init(&dev, SENSOR_PIN) != DHT_OK) {  // Correcting dht_init usage
        printf("Failed to initialize DHT sensor\n");
        return 1;
    }

    // Configure MQTT-SN (replace with actual configuration)
    mqttsn_publisher_init(&mqtt_conf, SERVER_ADDRESS, SERVER_PORT, EMCUTE_ID);

    // Main loop to read sensor data and publish every 2 seconds
    while (1) {
        read_and_publish();
        xtimer_sleep(2);
    }

    return 0;
}