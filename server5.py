from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# DATA FROM ESP
esp_data = {
    'analog_input': 0,
    'button': False,
    'motion':False,
}

# DATA FROM FLET APP
flet_data = {
    'led': False,
    'analog_output': 0,
    'servo_locked': False
}
html = """
    <!doctype html>
    <html>
      <head>
        <title>ESP32 Status</title>
        <meta http-equiv="refresh" content="1">
      </head>
      <body>
        <h1>ESP32 device status</h1>
        <div style="text-align:center;">
        <p style="colour:green;"><strong>
        <div style="text-align:left;">
        <p><strong>LED State:</strong>{{'ON' if flet_data['led'] else 'OFF'}}</p>
        <p><strong>Analog Input:</strong>{{flet_data['analog_output']}}</p>
        <p><strong>Servo Locked:</strong>{{'YES' if flet_data['servo_locked'] else 'NO'}}</p>
        
        <div style="text-align:center;">
        <p style="colour:green;"><strong>
        <div style="text-align:left;">
        <p><strong>Analog Input:</strong>{{esp_data['analog_input']}}</p>
        <p><strong>Button Pressed:</strong>{{'YES' if esp_data['button'] else 'NO' }}</p>
        <p><strong>Motion Detected:</strong>{{'YES' if esp_data['motion'] else 'NO' }}</p>


      </body>
    </html>
    """


@app.route('/')
def index():
    return render_template_string(html, esp_data=esp_data, flet_data=flet_data)

@app.route('/esp/update', methods=["POST"])
def update_from_esp():
    data = request.json
    esp_data["analog_input"] = data.get("analog_input", 0)
    esp_data["button"] = data.get("button", False)
    esp_data["motion"] = data.get("motion", False)
    return jsonify({'message': 'esp data received'}), 200


@app.route('/esp/control', methods=["GET"])
def send_to_esp():
    dict_to_esp = {
        'led': flet_data['led'],
        'analog_output': flet_data['analog_output'],
        'servo_locked': flet_data['servo_locked']
    }
    return jsonify(dict_to_esp), 200

@app.route('/flet/update', methods=["POST"])
def update_from_flet():
    data = request.json
    flet_data['led'] = data.get("led", False)
    flet_data['analog_output'] = data.get('analog_output', 0)
    flet_data['servo_locked'] = data.get('servo_locked', False)
    return jsonify({"message": "Flet data received"}), 200

@app.route('/dashboard', methods=["GET"])
def dashboard():
    dict_dashboard = {
        "flet": flet_data,
        "esp": esp_data
    }
    return jsonify(dict_dashboard)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)