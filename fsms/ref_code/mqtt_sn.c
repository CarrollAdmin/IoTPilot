#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>
#include "msg.h"
#include "net/emcute.h"
#include "thread.h"
#include <xtimer.h>

#ifndef EMCUTE_ID
#define EMCUTE_ID           ("gertrud")
#endif
#define EMCUTE_PRIO         (THREAD_PRIORITY_MAIN - 1)

#define NUMOFSUBS           (16U)
#define TOPIC_MAXLEN        (64U)
#define EMQX_SERVER_IP "47.102.103.1"  
static char stack[THREAD_STACKSIZE_DEFAULT];
static msg_t queue[8];

static emcute_sub_t subscriptions[NUMOFSUBS];
static char topics[NUMOFSUBS][TOPIC_MAXLEN];

static void *emcute_thread(void *arg)
{
    (void)arg;
    emcute_run(CONFIG_EMCUTE_DEFAULT_PORT, EMCUTE_ID);
    return NULL;    
}

static void on_pub(const emcute_topic_t *topic, void *data, size_t len)
{
    char *in = (char *)data;

    printf("### got publication for topic '%s' [%i] ###\n",
           topic->name, (int)topic->id);
    for (size_t i = 0; i < len; i++) {
        printf("%c", in[i]);
    }
    puts("");
}

static int connect_to_broker(const char *addr, uint16_t port, const char *will_topic, const char *will_message)
{
    sock_udp_ep_t gw = { .family = AF_INET, .port = port };

    int result = inet_pton(AF_INET, EMQX_SERVER_IP, &gw.addr.ipv4);
    if (result <= 0) {
        if (result == 0) {
            puts("Error: invalid IPv4 address format");
        } else {
            perror("inet_pton");
        }
    }

    size_t len = will_message ? strlen(will_message) : 0;
    if (emcute_con(&gw, true, will_topic, will_message, len, 0) != EMCUTE_OK) {
        printf("-----");
        printf("error: unable to connect to [%s]:%i\n", addr, (int)port);
        return 1;
    }
    
    printf("Successfully connected to gateway at [%s]:%i\n", addr, (int)port);

    return 0;
}

static int disconnect_from_broker(void)
{
    int res = emcute_discon();
    if (res == EMCUTE_NOGW) {
        puts("error: not connected to any broker");
        return 1;
    }
    else if (res != EMCUTE_OK) {
        puts("error: unable to disconnect");
        return 1;
    }
    puts("Disconnect successful");
    return 0;
}

static int publish_to_topic(const char *topic_name, const char *data, unsigned qos)
{
    emcute_topic_t t;
    unsigned flags = qos;

    t.name = topic_name;
    if (emcute_reg(&t) != EMCUTE_OK) {
        puts("error: unable to obtain topic ID");
        return 1;
    }

    if (emcute_pub(&t, data, strlen(data), flags) != EMCUTE_OK) {
        printf("error: unable to publish data to topic '%s [%i]'\n",
                t.name, (int)t.id);
        return 1;
    }

    printf("Published %" PRIuSIZE " bytes to topic '%s [%i]'\n",
           strlen(data), t.name, t.id);

    return 0;
}

static int subscribe_to_topic(const char *topic_name, unsigned qos)
{
    unsigned flags = qos;

    if (strlen(topic_name) > TOPIC_MAXLEN) {
        puts("error: topic name exceeds maximum possible size");
        return 1;
    }

    unsigned i = 0;
    for (; (i < NUMOFSUBS) && (subscriptions[i].topic.id != 0); i++) {}
    if (i == NUMOFSUBS) {
        puts("error: no memory to store new subscriptions");
        return 1;
    }

    subscriptions[i].cb = on_pub;
    strcpy(topics[i], topic_name);
    subscriptions[i].topic.name = topics[i];
    if (emcute_sub(&subscriptions[i], flags) != EMCUTE_OK) {
        printf("error: unable to subscribe to %s\n", topic_name);
        return 1;
    }

    printf("Now subscribed to %s\n", topic_name);
    return 0;
}

int main(void)
{
    puts("MQTT-SN example application\n");
    msg_init_queue(queue, ARRAY_SIZE(queue));
    memset(subscriptions, 0, (NUMOFSUBS * sizeof(emcute_sub_t)));
    thread_create(stack, sizeof(stack), EMCUTE_PRIO, 0, emcute_thread, NULL, "emcute");

    if (connect_to_broker("47.102.103.1", CONFIG_EMCUTE_DEFAULT_PORT, NULL, NULL) != 0) {
        return 1;
    }

    if (subscribe_to_topic("test/topic", EMCUTE_QOS_0) != 0) {
        return 1;
    }

    while (1) {
        if (publish_to_topic("test/topic", "Hello, world!", EMCUTE_QOS_0) != 0) {
            puts("Error publishing message");
        }
        xtimer_sleep(5); 
    }

    if (disconnect_from_broker() != 0) {
        return 1;
    }

    return 0;
}