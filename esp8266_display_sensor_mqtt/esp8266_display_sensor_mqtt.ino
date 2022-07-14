#include <Arduino.h>
#include <U8x8lib.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char *mqtt_broker = "192.168.178.53";
const char *topic = "mpu6050-sensor-node/sensor/mpu6050_accel_x/state";
const char *mqtt_username = "test";
const char *mqtt_password = "test";
const int mqtt_port = 1883;

const char *wifi_ssid = "";
const char *wifi_password = "";

String displayed_message = "";
String current_status = "";
// Pin 16   OLED Reset
// Pin 4,5  I2C

// use Board "Wemos D1 Mini R2", 80Mhz, 4(3)MB Flash, 921600baud to flash
U8X8_SSD1306_128X32_UNIVISION_HW_I2C u8x8(16);
WiFiClient espClient;
PubSubClient client(espClient);

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  float aFloat = *((float *)payload);
  if (aFloat > 2.5 && aFloat < 3.5)
  {
    current_status = "low";
  }
  else if (aFloat > 3.5 && aFloat < 6.0)
  {
    current_status = "middle";
  }
  else if (aFloat > 6.0 && aFloat < 3.5)
  {
    current_status = "high";
  }
  u8x8.clear();
  u8x8.setFont(u8x8_font_amstrad_cpc_extended_r);
  u8x8.draw2x2String(0, 2, current_status.c_str());
}

void setup()
{
  // Set software serial baud to 115200;
  Serial.begin(115200);
  // connecting to a WiFi network
  WiFi.begin(wifi_ssid, wifi_password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.println("Connecting to WiFi..");
  }
  Serial.println("Connected to the WiFi network");
  // connecting to a mqtt broker
  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  while (!client.connected())
  {
    String client_id = "esp8266-client-";
    client_id += String(WiFi.macAddress());
    Serial.printf("The client %s connects to the mqtt broker\n", client_id.c_str());
    if (client.connect(client_id.c_str(), mqtt_username, mqtt_password))
    {
      Serial.println("mqtt broker connected");
    }
    else
    {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }

  u8x8.begin();
  // subscribe
  client.subscribe(topic);
}

void loop(void)
{
  client.loop();
  delay(1000);
}
