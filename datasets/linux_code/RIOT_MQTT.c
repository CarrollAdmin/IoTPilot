/***************************************************************
Copyright  2024-2029. All rights reserved.
文件名  : test_01_Asynchronous.c
作者    : tangmingfei2013@126.com
版本    : V1.0
描述    : mqtt异步发布和订阅消息
日志    : 初版V1.0 2024/03/13
***************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "MQTTClient.h"
#include <unistd.h>
 
#define ADDRESS     "tcp://192.168.1.11:1883"
#define CLIENTID    "mqtt_ubuntu_asys"
#define TOPIC       "MQTTAsync"
#define PAYLOAD     "12.56"
#define QOS         1
#define TIMEOUT     10000L
 
#define USERNAME    "mqtt_ubuntu_user"
#define PASSWORD    "123456" 
 
static MQTTClient client;
static MQTTClient_deliveryToken deliveredtoken;
static MQTTClient_message pubmsg = MQTTClient_message_initializer;
static MQTTClient_deliveryToken token;
static MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
 
void delivered(void *context, MQTTClient_deliveryToken dt)
{
    printf("Message with token value %d delivery confirmed\n", dt);
    deliveredtoken = dt;
}
 
int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message)
{
    printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);
    
    return 1;
}
 
void connlost(void *context, char *cause)
{
    printf("\nConnection lost\n");
    printf("     cause: %s\n", cause);
}
 
void public_mqttMsg()
{
    int rc;
 
    pubmsg.payload = PAYLOAD;
    pubmsg.payloadlen = (int)strlen(PAYLOAD);
    pubmsg.qos = QOS;
    pubmsg.retained = 1;
    deliveredtoken = 0;
    if ((rc = MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to publish message, return code %d\n", rc);
        rc = EXIT_FAILURE;
    }
    else
    {
        printf("Waiting for publication of %s\n"
            "on topic %s for client with ClientID: %s\n",
            PAYLOAD, TOPIC, CLIENTID);
        while (deliveredtoken != token)
        {
            usleep(10000000L);
        }
    }
}
 
 
int main(int argc, char* argv[])
{
    int rc;
    
    if ((rc = MQTTClient_create(&client, ADDRESS, CLIENTID,
        MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to create client, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto exit;
    }
 
    if ((rc = MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to set callbacks, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto destroy_exit;
    }
 
    conn_opts.keepAliveInterval = 60;
    conn_opts.cleansession = 0;
    conn_opts.username = USERNAME;   //用户名
    conn_opts.password = PASSWORD;   //密码
    
    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to connect, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto destroy_exit;
    }
    
    while(1)
    {
        public_mqttMsg();
    }
 
    if ((rc = MQTTClient_disconnect(client, 10000)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to disconnect, return code %d\n", rc);
        rc = EXIT_FAILURE;
    }
 
destroy_exit:
    MQTTClient_destroy(&client);
 
exit:
    return rc;
}

/***************************************************************
Copyright  2024-2029. All rights reserved.
文件名  : test_01_Asynchronous.c
作者    : tangmingfei2013@126.com
版本    : V1.0
描述    : mqtt异步发布和订阅消息
日志    : 初版V1.0 2024/03/13
***************************************************************/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "MQTTClient.h"
#include <unistd.h>
 
#define ADDRESS     "tcp://192.168.1.11:1883"
#define CLIENTID    "mqtt_ubuntu_asys"
#define TOPIC       "MQTTAsync"
#define PAYLOAD     "12.56"
#define QOS         1
#define TIMEOUT     10000L
 
#define USERNAME    "mqtt_ubuntu_user"
#define PASSWORD    "123456" 
 
static MQTTClient client;
static MQTTClient_deliveryToken deliveredtoken;
static MQTTClient_message pubmsg = MQTTClient_message_initializer;
static MQTTClient_deliveryToken token;
static MQTTClient_connectOptions conn_opts = MQTTClient_connectOptions_initializer;
 
void delivered(void *context, MQTTClient_deliveryToken dt)
{
    printf("Message with token value %d delivery confirmed\n", dt);
    deliveredtoken = dt;
}
 
int msgarrvd(void *context, char *topicName, int topicLen, MQTTClient_message *message)
{
    printf("Message arrived\n");
    printf("     topic: %s\n", topicName);
    printf("   message: %.*s\n", message->payloadlen, (char*)message->payload);
    MQTTClient_freeMessage(&message);
    MQTTClient_free(topicName);
    
    return 1;
}
 
void connlost(void *context, char *cause)
{
    printf("\nConnection lost\n");
    printf("     cause: %s\n", cause);
}
 
void public_mqttMsg()
{
    int rc;
 
    pubmsg.payload = PAYLOAD;
    pubmsg.payloadlen = (int)strlen(PAYLOAD);
    pubmsg.qos = QOS;
    pubmsg.retained = 1;
    deliveredtoken = 0;
    if ((rc = MQTTClient_publishMessage(client, TOPIC, &pubmsg, &token)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to publish message, return code %d\n", rc);
        rc = EXIT_FAILURE;
    }
    else
    {
        printf("Waiting for publication of %s\n"
            "on topic %s for client with ClientID: %s\n",
            PAYLOAD, TOPIC, CLIENTID);
        while (deliveredtoken != token)
        {
            usleep(10000000L);
        }
    }
}
 
 
int main(int argc, char* argv[])
{
    int rc;
    
    if ((rc = MQTTClient_create(&client, ADDRESS, CLIENTID,
        MQTTCLIENT_PERSISTENCE_NONE, NULL)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to create client, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto exit;
    }
 
    if ((rc = MQTTClient_setCallbacks(client, NULL, connlost, msgarrvd, delivered)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to set callbacks, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto destroy_exit;
    }
 
    conn_opts.keepAliveInterval = 60;
    conn_opts.cleansession = 0;
    conn_opts.username = USERNAME;   //用户名
    conn_opts.password = PASSWORD;   //密码
    
    if ((rc = MQTTClient_connect(client, &conn_opts)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to connect, return code %d\n", rc);
        rc = EXIT_FAILURE;
        goto destroy_exit;
    }
    
    while(1)
    {
        public_mqttMsg();
    }
 
    if ((rc = MQTTClient_disconnect(client, 10000)) != MQTTCLIENT_SUCCESS)
    {
        printf("Failed to disconnect, return code %d\n", rc);
        rc = EXIT_FAILURE;
    }
 
destroy_exit:
    MQTTClient_destroy(&client);
 
exit:
    return rc;
}