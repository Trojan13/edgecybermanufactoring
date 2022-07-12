#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi
const char *ssid = "Velte Vunk";       // Enter your WiFi name
const char *password = "dKladHupdgZ!"; // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "192.168.178.53";
const char *topic = "esp8266/test";
const char *mqtt_username = "test";
const char *mqtt_password = "test";
const int mqtt_port = 1883;

/*#### MESSAGE QUEUE SETTINGS ####*/
#define birthMsg "CONNECTED"
#define willMsg "DISCONNECTED"

/*#### POWER CONTROLLER SETTINGS ####*/
String SensorName = "FSR12";
String mqttSeperator = "/mqtt";

/*#### DEFAULT VALUES ####*/
char bla2[60];
char bla3[60];

WiFiClient espClient;
PubSubClient client(espClient);

void setup()
{
  // Set software serial baud to 115200;
  Serial.begin(115200);
  // connecting to a WiFi network
  WiFi.begin(ssid, password);
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
    String basePath = "ArduinoData" + mqttSeperator + SensorName + mqttSeperator;
    String thisSensor = basePath + "Status";
    thisSensor.toCharArray(bla2, thisSensor.length() + 1);

    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    clientId.toCharArray(bla3, clientId.length() + 1);
    Serial.printf("The client %s connects to the public mqtt broker\n", clientId.c_str());
    if (client.connect(bla3, mqtt_username, mqtt_password, bla2, 1, 1, willMsg))
    {
      Serial.println("Public emqx mqtt broker connected");
    }
    else
    {
      Serial.print("failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
  // publish and subscribe
  client.publish(topic, "hello emqx");
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

void loop()
{
  client.loop();
}
