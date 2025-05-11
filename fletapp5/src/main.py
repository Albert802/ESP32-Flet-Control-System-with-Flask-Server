import flet as ft
import requests
import threading
import time

# Server configuration
SERVER_URL = "http://192.168.0.194:5000"
UPDATE_INTERVAL = 0.5  # Seconds between updates

def main(page: ft.Page):
    page.title = "ESP32 Control Panel"
    page.padding = 20
    page.window_width = 400
    page.window_height = 600

    # State variables
    led_state = False
    servo_locked = False
    analog_input = 0
    button_pressed = False

    # UI Elements
    led_button = ft.ElevatedButton(
        text="Turn LED ON",
        on_click=lambda e: toggle_led()
    )
    servo_button = ft.ElevatedButton(
        text="Lock Servo",
        on_click=lambda e: toggle_servo()
    )
    analog_display = ft.Text("Potentiometer: 0")
    button_display = ft.Text("Button: Not Pressed")

    # Functions
    def toggle_led():
        nonlocal led_state
        led_state = not led_state
        led_button.text = f"Turn LED {'OFF' if led_state else 'ON'}"
        send_flet_data()
        page.update()

    def toggle_servo():
        nonlocal servo_locked
        servo_locked = not servo_locked
        servo_button.text = f"{'Unlock' if servo_locked else 'Lock'} Servo"
        send_flet_data()
        page.update()

    def send_flet_data():
        data = {
            "led": led_state,
            "analog_output": 0,  # Not used in this app, but required by server
            "servo_locked": servo_locked
        }
        try:
            response = requests.post(f"{SERVER_URL}/flet/update", json=data)
            if response.status_code != 200:
                print("Error sending data to server")
        except requests.RequestException as e:
            print(f"Network error: {e}")

    def update_dashboard():
        while True:
            try:
                response = requests.get(f"{SERVER_URL}/dashboard")
                if response.status_code == 200:
                    data = response.json()
                    nonlocal analog_input, button_pressed

                    raw_value = data["esp"]["analog_input"]
                    analog_input = int((raw_value / 4095) * 49) + 1
                    button_pressed = data["esp"]["button"]
                    analog_display.value = f"Potentiometer: {analog_input}"
                    button_display.value = f"Button: {'Pressed' if button_pressed else 'Not Pressed'}"
                    page.update()
            except requests.RequestException as e:
                print(f"Dashboard update error: {e}")
            time.sleep(UPDATE_INTERVAL)

    # Layout
    page.add(
        ft.Text("ESP32 Control", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("Controls", size=18),
        led_button,
        servo_button,
        ft.Divider(),
        ft.Text("Sensor Inputs", size=18),
        analog_display,
        button_display
    )

    # Start background thread for dashboard updates
    threading.Thread(target=update_dashboard, daemon=True).start()

ft.app(target=main)