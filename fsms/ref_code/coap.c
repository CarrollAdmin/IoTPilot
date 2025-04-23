#include <stdio.h>
#include <string.h>
#include <arpa/inet.h>
#include "net/gcoap.h"
#include "net/sock/udp.h"
#include "od.h"
#include "ztimer.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"

#define EMQX_SERVER_IP "47.102.103.1"  
#define EMQX_SERVER_PORT 5683
#define EMQX_URI_PATH "/mqtt/coap/test"
#define PAYLOAD "hello,EMQX Cloud"

#define WIFI_SSID "EmNets-301"
#define WIFI_PASS "eagle402"

static void _resp_handler(const gcoap_request_memo_t *memo, coap_pkt_t *pdu, const sock_udp_ep_t *remote) {
    printf("##### Response Handler #####\n");
    printf("Response code: %u.%02u\n", pdu->hdr->code, pdu->hdr->code);
    if (memo->state == GCOAP_MEMO_TIMEOUT) {
        printf("gcoap: timeout for msg ID %02u\n", coap_get_id(pdu));
        return;
    }
    else if (memo->state == GCOAP_MEMO_RESP_TRUNC) {
        printf("gcoap: warning, incomplete response; continuing with the truncated payload\n");
    }
    else if (memo->state != GCOAP_MEMO_RESP) {
        printf("gcoap: error in response, state: %d\n", memo->state);
        return;
    }
    if (pdu->payload_len > 0) {
        printf("Response payload: ");
        for (size_t i = 0; i < pdu->payload_len; i++) {
            printf("%c", pdu->payload[i]);
        }
        printf("\n");
    } else {
        printf("No payload in response\n");
    }
    char addr_str[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &remote->addr.ipv4, addr_str, sizeof(addr_str));
    printf("Response from: %s:%d\n", addr_str, ntohs(remote->port));

    printf("success\n");
}

int wifi_is_connected(void) {
    wifi_ap_record_t ap_info;
    if (esp_wifi_sta_get_ap_info(&ap_info) == ESP_OK) {
        return 1;
    } else {
        return 0;
    }
}

void send_coap_request(void) {

    if (!wifi_is_connected()) {
        printf("WiFi is not connected\n");
        return;
    }else{
        printf("wifi connected\n");
    }
    uint8_t buf[CONFIG_GCOAP_PDU_BUF_SIZE];
    coap_pkt_t pdu;
    sock_udp_ep_t remote;
    remote.family = AF_INET;
    remote.port = EMQX_SERVER_PORT;
    int result = inet_pton(AF_INET, EMQX_SERVER_IP, &remote.addr.ipv4);
    if (result <= 0) {
        if (result == 0) {
            puts("Error: invalid IPv4 address format");
        } else {
            perror("inet_pton");
        }
        return;
    }
    gcoap_req_init(&pdu, buf, CONFIG_GCOAP_PDU_BUF_SIZE, COAP_METHOD_POST, EMQX_URI_PATH);
    coap_hdr_set_type(pdu.hdr, 1);
    coap_opt_add_format(&pdu, COAP_FORMAT_TEXT);
    size_t len = coap_opt_finish(&pdu, COAP_OPT_FINISH_PAYLOAD);
    printf("%d",len);
    if (sizeof(buf) - len >= strlen(PAYLOAD)) {
        memcpy(pdu.payload, PAYLOAD, strlen(PAYLOAD));
        len += strlen(PAYLOAD);
    } else {
        puts("Error: payload too large");
        return;
    }
    printf("Sending CoAP request to EMQX server at %s:%d ...\n", EMQX_SERVER_IP, EMQX_SERVER_PORT);
    ssize_t res = gcoap_req_send(&buf[0], len, &remote, _resp_handler, NULL, GCOAP_SOCKET_TYPE_UDP);
    printf("res:%d", res);
}

void wifi_init(void) {
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ret = esp_wifi_init(&cfg);
    if (ret != ESP_OK) {
        printf("Error: failed to initialize WiFi, error code: 0x%x\n", ret);
        return;
    }
    ret = esp_wifi_set_mode(WIFI_MODE_STA);
    if (ret != ESP_OK) {
        printf("Error: failed to set WiFi mode, error code: 0x%x\n", ret);
        return;
    }
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        },
    };
    ret = esp_wifi_set_config(WIFI_IF_STA, &wifi_config);
    if (ret != ESP_OK) {
        printf("Error: failed to set WiFi configuration, error code: 0x%x\n", ret);
        return;
    }
    ret = esp_wifi_start();
    if (ret != ESP_OK) {
        printf("Error: failed to start WiFi, error code: 0x%x\n", ret);
        return;
    }
    ret = esp_wifi_connect();
    if (ret != ESP_OK) {
        printf("Error: failed to connect WiFi, error code: 0x%x\n", ret);
        return;
    }
}

int main(void) {
    printf("Starting CoAP client example...\n");
    wifi_init();
    ztimer_sleep(ZTIMER_MSEC, 5 * MS_PER_SEC);
    while (1) {
        send_coap_request();
        ztimer_sleep(ZTIMER_MSEC, 1 * MS_PER_SEC);
    }

    return 0;
}