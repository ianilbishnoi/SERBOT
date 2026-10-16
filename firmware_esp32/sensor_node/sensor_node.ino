// ESP32 sensor node: MPU6050 IMU, HC-SR04 ultrasonic, DHT22, MQ gas sensor (analog).
// Publishes JSON to MQTT topic site/sensors every 100 ms; buzzes when site/alerts says DANGER.
// Libraries: PubSubClient, DHT sensor library (Adafruit).
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <DHT.h>

const char* WIFI_SSID = "YOUR_WIFI";
const char* WIFI_PASS = "YOUR_PASSWORD";
const char* MQTT_HOST = "192.168.1.10";   // laptop / Raspberry Pi running the MQTT broker

#define TRIG_PIN 5
#define ECHO_PIN 18
#define DHT_PIN  4
#define GAS_PIN  34
#define BUZZER_PIN 25
#define LED_PIN 26
#define MPU_ADDR 0x68

DHT dht(DHT_PIN, DHT22);
WiFiClient wifi;
PubSubClient mqtt(wifi);
float temp = NAN, hum = NAN;
unsigned long lastDht = 0, lastPub = 0;

void onMessage(char* topic, byte* payload, unsigned int len) {
  String s; for (unsigned int i = 0; i < len; i++) s += (char)payload[i];
  bool danger = s.indexOf("DANGER") >= 0;
  digitalWrite(BUZZER_PIN, danger); digitalWrite(LED_PIN, danger);
}

void connectAll() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) delay(300);
  mqtt.setServer(MQTT_HOST, 1883); mqtt.setCallback(onMessage);
  while (!mqtt.connected()) { if (!mqtt.connect("esp32-sensor-node")) delay(1000); }
  mqtt.subscribe("site/alerts");
}

bool readImu(float &ax, float &ay, float &az, float &gx, float &gy, float &gz) {
  Wire.beginTransmission(MPU_ADDR); Wire.write(0x3B);
  if (Wire.endTransmission(false) != 0) return false;
  Wire.requestFrom(MPU_ADDR, 14, true);
  int16_t r[7]; for (int i = 0; i < 7; i++) r[i] = (Wire.read() << 8) | Wire.read();
  ax = r[0] / 16384.0; ay = r[1] / 16384.0; az = r[2] / 16384.0;   // g
  gx = r[4] / 131.0;   gy = r[5] / 131.0;   gz = r[6] / 131.0;     // deg/s
  return true;
}

unsigned long readEchoUs() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10); digitalWrite(TRIG_PIN, LOW);
  return pulseIn(ECHO_PIN, HIGH, 30000);   // 0 = no echo
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT); pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT); pinMode(LED_PIN, OUTPUT);
  Wire.begin(); Wire.beginTransmission(MPU_ADDR); Wire.write(0x6B); Wire.write(0); Wire.endTransmission(true);
  dht.begin();
  connectAll();
}

void loop() {
  if (!mqtt.connected()) connectAll();
  mqtt.loop();
  if (millis() - lastDht > 2000) { temp = dht.readTemperature(); hum = dht.readHumidity(); lastDht = millis(); }
  if (millis() - lastPub >= 100) {
    lastPub = millis();
    float ax, ay, az, gx, gy, gz;
    if (!readImu(ax, ay, az, gx, gy, gz)) return;
    char buf[256];
    snprintf(buf, sizeof(buf),
      "{\"t\":%lu,\"ax\":%.4f,\"ay\":%.4f,\"az\":%.4f,\"gx\":%.3f,\"gy\":%.3f,\"gz\":%.3f,"
      "\"echo_us\":%lu,\"gas\":%d,\"temp\":%.1f,\"hum\":%.1f}",
      millis(), ax, ay, az, gx, gy, gz, readEchoUs(), analogRead(GAS_PIN),
      isnan(temp) ? 25.0 : temp, isnan(hum) ? 0.0 : hum);
    mqtt.publish("site/sensors", buf);
  }
}
