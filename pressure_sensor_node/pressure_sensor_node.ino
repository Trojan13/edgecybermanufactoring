#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// MQTT Broker
const char *mqtt_broker = "192.168.178.53";
const char *topic = "esp8266/fsrpressure";
const char *mqtt_username = "test";
const char *mqtt_password = "test";
const int mqtt_port = 1883;

const char *wifi_ssid = "";
const char *wifi_password = "";

const int FSR_1_PIN = 16;
const int FSR_2_PIN = 5;

int fsr1Read;
int fsr2Read;
bool sensorsSetup;

WiFiClient espClient;
PubSubClient client(espClient);

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

  setupSensors();
  // publish and subscribe
  client.subscribe(topic);
}

void callback(char *topic, byte *payload, unsigned int length)
{
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  for (int i = 0; i < length; i++)
  {
    Serial.print((char)payload[i]);
  }
  Serial.println();
  Serial.println("-----------------------");
}

void setupSensors()
{
  pinMode(FSR_1_PIN, OUTPUT);
  pinMode(FSR_2_PIN, OUTPUT);
  while (!Serial)
    delay(10);

  sensorsSetup = true;
  client.publish(topic, "FSR Sensors Setup Finished");
}

int analogReadOnDigital(int readPin)
{
  if (readPin == 1)
  {
    digitalWrite(FSR_1_PIN, HIGH);
    digitalWrite(FSR_2_PIN, LOW);
  }
  else
  {
    digitalWrite(FSR_2_PIN, HIGH);
    digitalWrite(FSR_1_PIN, LOW);
  }

  return analogRead(0);
}

void loop()
{
  client.loop();
  if (sensorsSetup)
  {

    fsr1Read = analogReadOnDigital(1);
    delay(100);
    fsr2Read = analogReadOnDigital(2);
    delay(100);

    StaticJsonDocument<64> doc;

    doc["type"] = "fsr";
    doc["fsr1"] = fsr1Read;
    doc["fsr2"] = fsr2Read;

    char output[64];
    serializeJson(doc, output);
    client.publish(topic, output);
    delay(100);
  }
}
