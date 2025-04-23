#include "ztimer.h"
#include "xtimer.h"
#include "timex.h"
#include "time_units.h"
#include "paho_mqtt.h"
#include "mutex.h"
#include "mma8x5x_regs.h"
#include "mma8x5x.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "dht_params.h"
#include "dht.h"
#include "MQTTClient.h"

#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define PUBLISH_INTERVAL (5U * US_PER_SEC)  // Publish every 5 seconds

static MQTTClient client;
static Network network;
static unsigned char sendbuf[100], readbuf[100];

void mqtt_publish(MQTTClient *client) {

    MQTTMessage message;
    char *state_msg = "work";
    message.qos = QOS0;
    message.retained = 0;
    message.payload = (void *)state_msg;
    message.payloadlen = strlen(state_msg);

    MQTTPublish(client, "state", &message);
}

static void *publish_thread(void *arg) {
    (void)arg;
    while (1) {
        mqtt_publish(&client);
        ztimer_sleep(ZTIMER_USEC, PUBLISH_INTERVAL);
    }
    return NULL;
}

int main(void) {

    ztimer_sleep(ZTIMER_USEC, PUBLISH_INTERVAL*2); //wait for WIFI connected
    NetworkInit(&network);
    MQTTClientInit(&client, &network, 1000, sendbuf, sizeof(sendbuf), readbuf, sizeof(readbuf));
   

    while(1){
        NetworkConnect(&network, MQTT_BROKER_IP, MQTT_BROKER_PORT);
        MQTTPacket_connectData data = MQTTPacket_connectData_initializer;
        int ret = MQTTConnect(&client, &data);
        printf("%d\n", ret);
        if(ret == 0) break;
        ztimer_sleep(ZTIMER_MSEC, 1 * MS_PER_SEC);
    }

    publish_thread(NULL);

    return 0;
}
