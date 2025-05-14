#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char* ssid = "Galaxy";
const char* password = "hiwc2593";

const char* serverIP = "192.168.208.49";
const int serverPort = 5000;
String serverBaseURL = "http://" + String(serverIP) + ":" + String(serverPort);

#define BUTTON_PIN 12
#define LEDPIN 27
#define ANALOG_PIN 34
#define SERVO_PIN 25
#define PIR_PIN 35

Servo myServo;

unsigned long previousMillis = 0;
const long interval = 500; // ms

int lastPirVal = LOW;

void setup() {
  Serial.begin(115200);

  pinMode(BUTTON_PIN, INPUT);
  pinMode(LEDPIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);

  myServo.attach(SERVO_PIN);
  myServo.write(0); // Start with servo unlocked

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // 1. Read sensor values
    bool buttonPressed = digitalRead(BUTTON_PIN) == HIGH;
    int analogInput = analogRead(ANALOG_PIN);
    int pirState = digitalRead(PIR_PIN);

    // PIR motion detection logging
    if (pirState == HIGH && lastPirVal == LOW) {
      Serial.println("Motion detected!");
      lastPirVal = HIGH;
    } else if (pirState == LOW && lastPirVal == HIGH) {
      Serial.println("Motion ended!");
      lastPirVal = LOW;
    }

    // 2. Send ESP sensor data to server
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;

      http.begin(serverBaseURL + "/esp/update");
      http.addHeader("Content-Type", "application/json");

      StaticJsonDocument<200> doc;
      doc["analog_input"] = analogInput;
      doc["button"] = buttonPressed;
      doc["motion"] = pirState;

      String requestBody;
      serializeJson(doc, requestBody);
      int httpResponseCode = http.POST(requestBody);
      if (httpResponseCode > 0) {
        Serial.println("ESP data sent.");
      } else {
        Serial.printf("POST error: %d\n", httpResponseCode);
      }
      http.end();

      // 3. Receive control data from server
      http.begin(serverBaseURL + "/esp/control");
      int code = http.GET();
      if (code == 200) {
        String payload = http.getString();
        StaticJsonDocument<200> controlDoc;
        DeserializationError error = deserializeJson(controlDoc, payload);
        if (!error) {
          bool ledState = controlDoc["led"];
          int analogOut = controlDoc["analog_output"] | 0;
          bool servoLocked = controlDoc["servo_locked"];

          digitalWrite(LEDPIN, ledState ? HIGH : LOW);

          // Use PWM if needed (optional):
          // ledcWrite(channel, analogOut); // configure PWM if you go this route

          myServo.write(servoLocked ? 90 : 0);

          Serial.printf("LED: %s | Servo: %s | Analog Out: %d\n",
                        ledState ? "ON" : "OFF",
                        servoLocked ? "Locked" : "Unlocked",
                        analogOut);
        } else {
          Serial.println("JSON parsing error.");
        }
      } else {
        Serial.printf("GET error: %d\n", code);
      }
      http.end();
    }
  }
}
