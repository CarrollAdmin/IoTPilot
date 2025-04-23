
// Ready: DHT11 logic; DHTT headers; MQTT logic; 1/2 MQTT headers
// not ready: 0
// minimal code modification: 0%


#include <dht.h>
#include <dht_params.h>
#include <esp_system.h>
#include <esp_wifi.h>
#include <nvs_flash.h>
#include <MQTTClient.h>
#include <paho_mqtt.h>
#include <stdio.h>
#include <stdlib.h>
#include <xtimer.h>

#define WIFI_SSID "your_wifi_ssid"
#define WIFI_PASS "your_wifi_password"
#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define DHT_PIN GPIO_NUM_4
#define DHT_TYPE DHT_TYPE_DHT11

static const char *TAG = "MQTT_DHT11";

void mqtt_publish_temperature_humidity(float temperature, float humidity) {
    MQTTClient client;
    Network network;
    unsigned char sendbuf[80], readbuf[80];
    int rc = 0;

    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));

    if ((rc = NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT)) != 0) {
        printf("Failed to connect to network, return code %d\n", rc);
        return;
    }

    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32_client";

    if ((rc = MQTTConnect(&client, &connectData)) != 0) {
        printf("Failed to connect to MQTT broker, return code %d\n", rc);
        return;
    }

    char payload[50];
    snprintf(payload, sizeof(payload), "{\"temperature\": %.2f, \"humidity\": %.2f}", temperature, humidity);

    if ((rc = MQTTPublish(&client, "sensor/dht11", payload)) != 0) {
        printf("Failed to publish message, return code %d\n", rc);
    }

    MQTTDisconnect(&client);
    NetworkDisconnect(&network);
}

void app_main(void) {
    nvs_flash_init();

    dht_t dev;
    dht_init(&dev, DHT_PIN, DHT_TYPE);

    while (1) {
        int16_t temperature, humidity;
        if (dht_read(&dev, &temperature, &humidity) == 0) {
            printf("Temperature: %d, Humidity: %d\n", temperature, humidity);
            mqtt_publish_temperature_humidity(temperature / 10.0, humidity / 10.0);
        } else {
            printf("Failed to read from DHT sensor\n");
        }
        xtimer_sleep(10);
    }
}