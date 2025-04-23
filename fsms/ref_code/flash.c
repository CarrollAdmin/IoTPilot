#include <stdio.h>
#include "nvs_flash.h"
#include "nvs.h"
#include "xtimer.h"

void flash(void *arg) {
    // Initialize NVS
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);

    // Open NVS handle
    printf("\n");
    printf("Opening Non-Volatile Storage (NVS) handle... ");
    nvs_handle_t my_handle;
    err = nvs_open("storage", NVS_READWRITE, &my_handle);
    if (err != ESP_OK) {
        printf("Error (%d) opening NVS handle!\n", err);
    } else {
        printf("Done\n");

        // Write temperature to NVS
        int temp = *((int*)arg);
        err = nvs_set_i32(my_handle, "temperature", temp);
        printf((err != ESP_OK) ? "Failed!\n" : "Done\n");

        // Commit updates in NVS
        printf("Committing updates in NVS ... ");
        err = nvs_commit(my_handle);
        printf((err != ESP_OK) ? "Failed!\n" : "Done\n");

        // Close NVS handle
        nvs_close(my_handle);
    }

    printf("\n");
}

int main(void) {
    int temp = 22;

    // Continuously perform flash operations
    while (1) {
        flash(&temp);
        xtimer_sleep(1); 
    }

    return 0;
}
