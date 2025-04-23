// Ready: DHT11 logic; DHTT headers;
// not ready:  MQTT headers;; MQTT logic
// minimal code modification: 60%


#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ztimer.h>
#include <net/sock/udp.h>
#include <net/emcute.h>
#include <periph/i2c.h>
#include <periph/gpio.h>
#include <dht.h>

#define SERVER_ADDR         "47.102.103.1"
#define SERVER_PORT         1883
#define PUB_TOPIC           "temp_hum_data"
#define I2C_PORT            I2C_DEV(0)
#define DHT_PIN             GPIO_PIN(0, 4)

static dht_t dev;

void dht11_init(void) {
    dht_params_t params;
    params.type = DHT11;
    params.pin = DHT_PIN;
    dev.params = params;
}

int publish_data(void *arg) {
    (void)arg;

    char message[64];
    int16_t temp, hum;

    if (dht_read(&dev, &temp, &hum) == DHT_OK) {
        snprintf(message, sizeof(message), "Temperature: %d.%d°C Humidity: %d.%d%%", 
                 temp / 10, temp % 10, hum / 10, hum % 10);
        printf("%s\n", message);

        emcute_topic_t topic;
        topic.name = PUB_TOPIC;
        
        int res = emcute_pub(&topic, message, strlen(message), EMCUTE_QOS_0);
        if (res != EMCUTE_OK) {
            printf("Error publishing data\n");
            return -1;
        }
    } else {
        printf("Error reading sensor data\n");
        return -1;
    }
    return 0;
}

int main(void) {
    dht11_init();

    sock_udp_ep_t gw = {.family = AF_INET, .port = SERVER_PORT };
    inet_pton(AF_INET, SERVER_ADDR, &gw.addr.ipv4);

    if (emcute_con(&gw, true, NULL, NULL, 0, 0) != EMCUTE_OK) {
        puts("[MQTT] Connection failed\n");
        return 1;
    }

    while (1) {
        publish_data(NULL);
        ztimer_sleep(ZTIMER_MSEC, 10000); // Sleep for 10 seconds
    }

    return 0;
}