#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "event/periodic_callback.h"
#include "event/thread.h"

static void memory_usage_callback(void *ctx) {
    
    multi_heap_info_t heap_info;
    heap_caps_get_info(&heap_info, MALLOC_CAP_DEFAULT);

    printf("Free heap size: %d bytes\n", heap_info.total_free_bytes);
    printf("Largest free block: %d bytes\n", heap_info.largest_free_block);
    printf("Total allocated size: %d bytes\n", heap_info.total_allocated_bytes);
}

int main(void) {

    event_periodic_callback_t memory_check_event;

    event_periodic_callback_init(&memory_check_event, ZTIMER_MSEC, EVENT_PRIO_MEDIUM, memory_usage_callback, NULL);

    event_periodic_callback_set_count(&memory_check_event, 0);

    event_periodic_callback_start(&memory_check_event, 1000);

    ztimer_sleep(ZTIMER_MSEC, 10000);

    return 0;
}
