
#include "dht.h"
#include "dht_params.h"
#include "event/thread.h"
#include "periph/gpio.h"
#include "periph/i2c.h"
#include "thread.h"
#include "periph/rtc.h"
#include "ztimer.h"
#include <stdio.h>

#define DHT_PIN GPIO_PIN(0, 2)
#define STACK_SIZE 256
#define PRIORITY 5

static dht_t dht_dev;

void read_dht(void) {
    int16_t temp, hum;
    while (1) {
        if (dht_read(&dht_dev, &temp, &hum) == 0) {
            printf("Temperature: %d.%d C, Humidity: %d.%d %%\n", temp / 10, temp % 10, hum / 10, hum % 10);
        } else {
            printf("Failed to read from DHT sensor\n");
        }
        ztimer_sleep(ZTIMER_MSEC, 5000);
    }
}

int main(void) {
    dht_params_t dht_params = {
        .pin = DHT_PIN,
        .type = DHT11
    };

    if (dht_init(&dht_dev, &dht_params) != DHT_OK) {
        printf("DHT11 initialization failed\n");
        return 1;
    }

    char stack[STACK_SIZE];
    thread_create(stack, STACK_SIZE, PRIORITY, 0, (thread_task_func_t)read_dht, NULL, "dht_reader");

    return 0;
}
