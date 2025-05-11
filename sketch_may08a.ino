#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

const char* ssid = "OPPO_D11EA9_2.4G";
const char* password ="wyF3yPuY";

const char* serverIP = "192.168.0.194";



const int serverPort = 5000;
String serverBaseURL = "http://" + String(serverIP) + ":" + String(serverPort);

#define BUTTON_PIN 12
#define LEDPIN 27
#define ANALOG_PIN 34
#define SERVO_PIN 25

Servo myServo;

unsigned long previousMillis = 0;
const long interval = 500; // Update interval in ms

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT);
  pinMode(LEDPIN, OUTPUT);
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

    // 2. Send ESP sensor data to server
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;

      // Send sensor data
      http.begin(serverBaseURL + "/esp/update");
      http.addHeader("Content-Type", "application/json");

      StaticJsonDocument<200> doc;
      doc["analog_input"] = analogInput;
      doc["button"] = buttonPressed;

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
          int analogOut = controlDoc["analog_output"] | 0;  // Optional field
          bool servoLocked = controlDoc["servo_locked"];

          digitalWrite(LEDPIN, ledState ? HIGH : LOW);
          // analogWrite only works on certain PWM-capable pins; confirm for pin 27
          // analogWrite(LEDPIN, analogOut); // Optional: comment out if not using

          // Move servo based on lock state
          if (servoLocked) {
            myServo.write(90); // Locked
          } else {
            myServo.write(0);  // Unlocked
          }

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
