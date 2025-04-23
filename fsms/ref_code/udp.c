#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>
#include <errno.h>  
#include "xtimer.h"
#include "esp_wifi.h"

#define DEFAULT_NUM_SENDS 1000
#define DEFAULT_DELAY_US 100000

int wifi_is_connected(void) {
    wifi_ap_record_t ap_info;
    if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
        return 1;
    } else {
        return 0;
    }
}

static int udp_send(char *addr_str, char *port_str, const char *data,
                    unsigned int num, unsigned int delay)
{
    struct sockaddr_in dest_addr;
    size_t data_len = strlen(data);
    int sock;

    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    uint16_t port = atoi(port_str);
    dest_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, addr_str, &dest_addr.sin_addr) <= 0) {
        perror("inet_pton");
        return 1;
    }

    if ((sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) < 0) {
        perror("socket creation failed");
        return 1;
    }

    for (unsigned int i = 0; i < num; i++) {
        if (!wifi_is_connected()) {
            printf("WiFi is not connected\n");
        } else {
            printf("WiFi connected\n");
        }
        int re = sendto(sock, data, data_len, 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
        printf("%d\n",re);
        if (re < 0) {
            printf("sendto failed: %s (errno: %d)\n", strerror(errno), errno);
        } else {
            printf("Success: sent %d bytes to %s:%d\n", data_len, addr_str, port);
        }
        xtimer_usleep(delay);
    }

    close(sock);
    return 0;
}

int main(void)
{
    char *addr_str = "47.102.103.1";  
    char *port = "20001";                    
    char *data = "Hello, RIOT!";        
    unsigned int num = DEFAULT_NUM_SENDS;    
    unsigned int delay = DEFAULT_DELAY_US;   

    return udp_send(addr_str, port, data, num, delay);
}