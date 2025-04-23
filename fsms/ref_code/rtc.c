#include <stdio.h>
#include <time.h>
#include "periph/rtc.h"
#include "xtimer.h"

#define ALARM_PERIOD (5U) // Set alarm period to 5 seconds

static void alarm_callback(void *arg) {
    printf("Alarm triggered!\n");
}

int main(void) {
    struct tm time = {0};
    mutex_t rtc_mtx = MUTEX_INIT_LOCKED;

    printf("RTC Alarm Test Application\n");

    rtc_init();

    rtc_get_time(&time);
    printf("Current RTC time: %04d-%02d-%02d %02d:%02d:%02d\n",
           time.tm_year + 1900, time.tm_mon + 1, time.tm_mday,
           time.tm_hour, time.tm_min, time.tm_sec);

    time.tm_year = 2024 - 1900; 
    time.tm_mon  = 6 - 1;       
    time.tm_mday = 1;
    time.tm_hour = 0;
    time.tm_min  = 0;
    time.tm_sec  = 0;
    rtc_set_time(&time);
    printf("Time set to: %04d-%02d-%02d %02d:%02d:%02d\n",
           time.tm_year + 1900, time.tm_mon + 1, time.tm_mday,
           time.tm_hour, time.tm_min, time.tm_sec);


    rtc_get_time(&time);
    time.tm_sec += ALARM_PERIOD;
    rtc_set_alarm(&time, alarm_callback, &rtc_mtx);
    printf("Alarm set to: %04d-%02d-%02d %02d:%02d:%02d\n",
           time.tm_year + 1900, time.tm_mon + 1, time.tm_mday,
           time.tm_hour, time.tm_min, time.tm_sec);

    while (1) {
        xtimer_sleep(1); 
        if (mutex_trylock(&rtc_mtx) == 0) {
            break;
        }
    }

    printf("Application finished.\n");

    return 0;
}
