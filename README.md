# IoTPilot Tutorial

**Step 1:** User→ Give me a MQTT application, which need to update local device state (ready or not ready) to Cloud EMQX. It builds on RIOT OS and runs on ESP32. 

IoTPilot→ Exec. `python3 iotpilot.py --model="gpt-4o" --iscontext=True --isexecution=True --userproblem="I need to develop a RIOT-based MQTT program runing on ESP32. It needs to update local device state (ready or not ready) to Cloud EMQX Broker."` 

```c
#include <ztimer.h>
#include <timex.h>
#include <time_units.h>
#include <thread.h>
#include <paho_mqtt.h>
#include <arpa/inet.h>
#include <MQTTClient.h>

/* Function to update the local device state to Cloud EMQX Broker using MQTT */
int main(void) {
    Network network;
    MQTTClient client;
    unsigned int command_timeout_ms = 5000;
    uint8_t sendbuf[100], readbuf[100];

    // Initialize the network struct
    NetworkInit(&network);

    // Connect to the network (replace with actual address and port)
    char *address = "broker.emqx.io";
    int port = 1883;
    int rc = NetworkConnect(&network, address, port);

    if (rc != 0) {
        printf("Network connection failed\n");
        return -1;
    }

    // Initialize MQTT client with unsigned char buffers
    MQTTClientInit(&client, &network, command_timeout_ms,
                   (unsigned char*)sendbuf, sizeof(sendbuf),
                   (unsigned char*)readbuf, sizeof(readbuf));

    // Connect the MQTT client to the broker
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32-client";

    rc = MQTTConnect(&client, &connectData);

    if (rc != 0) {
        printf("MQTT connection failed\n");
        return -1;
    }

    printf("MQTT connection successful\n");

    // Publish a message about the device state
    const char* topic = "device/state";
    MQTTMessage message;
    message.qos = 1;
    message.retained = 0;
    message.payload = "ready";  // or "not ready" based on the device state
    message.payloadlen = strlen((char*)message.payload);

    rc = MQTTPublish(&client, topic, &message);

    if (rc != 0) {
        printf("MQTT Publish failed\n");
        return -1;
    }

    printf("Device state published successfully\n");

    return 0;
}
```

**Step 2:** user→My MQTT broker address is "47.102.103.1”, port is “1883”.   [user point：(line 36-37) ]

IoTPilot→ Exec.`python3 iotpilot.py --model="gpt-4o" --iscontext=True --isexecution=True --userproblem="The current code: {curr_code}. You need to modify the current code line 36-37 by {new prompt}"` 

```c
#include <ztimer.h>
#include <timex.h>
#include <time_units.h>
#include <thread.h>
#include <paho_mqtt.h>
#include <arpa/inet.h>
#include <MQTTClient.h>

/* Function to update the local device state to Cloud EMQX Broker using MQTT */
int main(void) {
    Network network;
    MQTTClient client;
    unsigned int command_timeout_ms = 5000;
    uint8_t sendbuf[100], readbuf[100];

    // Initialize the network struct
    NetworkInit(&network);

    // Connect to the network with the correct IP address
    char *address = "47.102.103.1";
    int port = 1883;
    int rc = NetworkConnect(&network, address, port);

    if (rc != 0) {
        printf("Network connection failed\n");
        return -1;
    }

    // Initialize MQTT client with unsigned char buffers
    MQTTClientInit(&client, &network, command_timeout_ms,
                   (unsigned char*)sendbuf, sizeof(sendbuf),
                   (unsigned char*)readbuf, sizeof(readbuf));

    // Connect the MQTT client to the broker
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32-client";

    rc = MQTTConnect(&client, &connectData);

    if (rc != 0) {
        printf("MQTT connection failed\n");
        return -1;
    }

    printf("MQTT connection successful\n");

    // Publish a message about the device state
    const char* topic = "device/state";
    MQTTMessage message;
    message.qos = 1;
    message.retained = 0;
    message.payload = "ready";  // or "not ready" based on the device state
    message.payloadlen = strlen((char*)message.payload);

    rc = MQTTPublish(&client, topic, &message);

    if (rc != 0) {
        printf("MQTT Publish failed\n");
        return -1;
    }

    printf("Device state published successfully\n");

    return 0;
}
```

**Step3:** user→We should upload local device state to EMQX broker each five seconds. [user point：(line 71-73) ]

IoTPilot→Exec.`python3 iotpilot.py --model="gpt-4o" --iscontext=True --isexecution=True --userproblem="The current code: {curr_code}. You need to modify the current code line 71-73 by {new prompt}"` 

```c
#include <ztimer.h>
#include <timex.h>
#include <time_units.h>
#include <thread.h>
#include <paho_mqtt.h>
#include <arpa/inet.h>
#include <MQTTClient.h>

/* Function to update the local device state to Cloud EMQX Broker using MQTT */
int main(void) {
    Network network;
    MQTTClient client;
    unsigned int command_timeout_ms = 5000;
    uint8_t sendbuf[100], readbuf[100];

    // Initialize the network struct
    NetworkInit(&network);

    // Connect to the network (replace with actual address and port)
    char *address = "47.102.103.1";
    int port = 1883;
    int rc = NetworkConnect(&network, address, port);

    if (rc != 0) {
        printf("Network connection failed\n");
        return -1;
    }

    // Initialize MQTT client with unsigned char buffers
    MQTTClientInit(&client, &network, command_timeout_ms,
                   (unsigned char*)sendbuf, sizeof(sendbuf),
                   (unsigned char*)readbuf, sizeof(readbuf));

    // Connect the MQTT client to the broker
    MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
    connectData.MQTTVersion = 3;
    connectData.clientID.cstring = "esp32-client";

    rc = MQTTConnect(&client, &connectData);

    if (rc != 0) {
        printf("MQTT connection failed\n");
        return -1;
    }

    printf("MQTT connection successful\n");

    // Publish a message about the device state every 5 seconds
    const char* topic = "device/state";
    MQTTMessage message;
    message.qos = 1;
    message.retained = 0;
    message.payload = "ready";  // or "not ready" based on the device state
    message.payloadlen = strlen((char*)message.payload);

    while(1) {
        rc = MQTTPublish(&client, topic, &message);
        if (rc != 0) {
            printf("MQTT Publish failed\n");
            return -1;
        }

        printf("Device state published successfully\n");

        // Sleep for 5 seconds
        xtimer_sleep(5);
    }

    return 0;
}
```