// Ready: DHT11 logic; DHTT headers
// not ready:  MQTT headers;MQTT logic;
// minimal code modification: 60%
// incorrect MQTT publish

#include <xtimer.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <dht.h>
#include <MQTTPacket.h>

#define DHT_PIN 17
#define MQTT_BROKER_IP "47.102.103.1"
#define MQTT_BROKER_PORT 1883
#define PUBLISH_TOPIC "sensor/dht"
#define CLIENT_ID "riot_dht_client"
#define MESSAGE_BUF_SIZE 234

static unsigned char sendbuf[200];
dht_t dev;

void mqtt_publish_temp_hum(int16_t temp, int16_t hum) {
  // This code handles MQTT publish for temperature and humidity
  // create a connection message
  MQTTPacket_connectData connectData = MQTTPacket_connectData_initializer;
  connectData.clientID.cstring = CLIENT_ID;
  int connect_len = MQTTSerialize_connect(sendbuf, sizeof(sendbuf), &connectData);

  // Allocate buffer to store the message
  char message[MESSAGE_BUF_SIZE];
  snprintf(message, sizeof(message), \
    "Temperature: %d.%d°C, Humidity: %d.%d%% RH", \
    temp / 10, temp % 10, hum / 10, hum % 10);

  MQTTString topicString = MQTTString_initializer;
  topicString.cstring = PUBLISH_TOPIC;
  int publish_len = MQTTSerialize_publish(sendbuf, sizeof(sendbuf), 0, 0, 0, 0, topicString, (unsigned char*)message, strlen(message));

  // Disconnect the MQTT session
  int disconnect_len = MQTTSerialize_disconnect(sendbuf, sizeof(sendbuf));
  // Placeholder for actual send function to the broker
  printf("Sending connect packet to MQTT broker, length: %d\n", connect_len);
  printf("Sending publish packet to MQTT broker, length: %d\n", publish_len);
  printf("Sending disconnect packet to MQTT broker, length: %d\n", disconnect_len);
}

void read_dht_sensor(void) {
  int16_t temp, hum;
  dht_params_t params = { .pin = DHT_PIN, .type = DHT11 };

  if (dht_init(&dev, &params) != DHT_OK) {
    printf("Error: unable to initialize DHT11\n");
    return;
  }

  while (1) {
    if (dht_read(&dev, &temp, &hum) != DHT_OK) {
      printf("Error: unable to read DHT11 data\n");
    } else {
      printf("Temperature: %d.%d°C, Humidity: %d.%d%% RH\n", temp / 10, temp % 10, hum / 10, hum % 10);
      mqtt_publish_temp_hum(temp, hum);
    }
    xtimer_sleep(30);
  }
}

int main(void) {
  read_dht_sensor();
  return 0;
}