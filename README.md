#ESP32-Flet Control System
This project showcases a full-stack IoT system where an ESP32 microcontroller communicates with a Flask server, which then interacts with a Flet (Python GUI) application to monitor and control physical components in real time.


🧩 Project Overview
This system allows:

Remote control of an LED and servo motor connected to the ESP32.

Real-time updates of sensor values: potentiometer (analog input) and a button press.

Two-way communication between the ESP32 and a GUI built with Flet.

Optional web dashboard (via Flask) to view device status on a browser.

🛠️ Components
Hardware:
ESP32 Development Board

Potentiometer (connected to analog pin 34)

Button (digital pin 12)

LED (digital pin 27)

Servo Motor (PWM pin 25)

Wi-Fi Connection

Software:
Python 3.x

Flask (REST API)

Flet (GUI)

Arduino IDE (for ESP32)

ArduinoJson, WiFi, HTTPClient, ESP32Servo libraries

🔧 Setup Instructions
1. ESP32 Firmware
Flash the ESP32 with the provided Arduino code.

Update these lines with your Wi-Fi credentials and server IP:

cpp
Copy
Edit
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";
const char* serverIP = "YOUR_PC_LOCAL_IP"; // e.g., 192.168.0.x
Install the following Arduino libraries if missing:

ESP32Servo

ArduinoJson

2. Python Environment
Create a virtual environment:
bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
Install dependencies:
bash
Copy
Edit
pip install flask flask-cors flet requests
3. Run Flask Server
bash
Copy
Edit
python server.py
This will start the server at http://<your-ip>:5000.

4. Run Flet GUI
bash
Copy
Edit
python flet_app.py
This opens the control panel to toggle the LED, control the servo, and see live sensor data.

🌐 Endpoints (Flask API)
Endpoint	Method	Description
/esp/update	POST	Receives sensor data from ESP32
/esp/control	GET	Sends control commands to ESP32
/flet/update	POST	Receives control input from Flet app
/dashboard	GET	Returns full ESP + Flet status (JSON)
/	GET	Returns HTML dashboard (browser view)

📺 Screenshots (Optional)
Add screenshots of:

Flet GUI

Flask HTML dashboard

Serial Monitor Output (ESP32)

🧠 Learning Highlights
Bidirectional communication between microcontroller and GUI.

Building REST APIs for real-time IoT systems.

Simple GUI with Flet for non-web developers.

Understanding how to integrate ESP32 with Python backends.

📂 Folder Structure
bash
Copy
Edit
├── flet_app.py          # Flet control panel
├── server.py            # Flask backend
├── esp_code.ino         # ESP32 Arduino code
└── README.md
📜 License
This project is open source under the MIT License.
