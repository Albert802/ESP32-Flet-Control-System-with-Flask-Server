import flet as ft
import requests
import threading
import time
from datetime import datetime

# Server configuration
SERVER_URL = "http://192.168.208.49:5000"
UPDATE_INTERVAL = 0.5  # Seconds between updates
TABLE_UPDATE_INTERVAL = 10  # Seconds between table updates


def main(page: ft.Page):
    page.title = "ESP32 Control Panel"
    page.padding = 20
    page.window_width = 600
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO  # Enable page scrolling

    # State variables
    led_state = False
    servo_locked = False
    analog_input = 0
    last_override_value = 0  # Track potentiometer value during override
    is_manual_override = False  # Flag to check if in manual mode
    button_pressed = False
    motion_detected = False
    sensor_history = []

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
    motion_display = ft.Text("Motion: Not Detected")

    # Visual indicator for motion detection
    motion_indicator = ft.Container(
        width=20,
        height=20,
        border_radius=10,
        bgcolor=ft.colors.RED_200
    )
    motion_row = ft.Row(
        controls=[
            motion_display,
            motion_indicator
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START
    )

    # Create a data table for sensor history
    sensor_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Timestamp")),
            ft.DataColumn(ft.Text("Potentiometer")),
            ft.DataColumn(ft.Text("Motion")),
        ],
        rows=[],
    )

    # Put the table in a container with a heading and border
    table_container = ft.Column(
        controls=[
            ft.Text("Sensor History (Updates every 10 seconds)", size=16, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=sensor_table,
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                padding=10,
            )
        ],
        spacing=10
    )

    # Main content column with scrolling
    main_content = ft.Column(
        controls=[
            ft.Text("ESP32 Control", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Controls", size=18),
            led_button,
            servo_button,
            ft.Divider(),
            ft.Text("Sensor Inputs", size=18),
            analog_display,
            button_display,
            motion_row,
            ft.Divider(),
            table_container
        ],
        spacing=20,
        scroll=ft.ScrollMode.AUTO,  # Enable scrolling for this column
        expand=True  # Allow the column to expand to available space
    )

    # Functions
    def toggle_led():
        nonlocal led_state, is_manual_override, last_override_value
        led_state = not led_state
        is_manual_override = True  # Enter manual override mode
        last_override_value = analog_input  # Save current potentiometer value
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
            "analog_output": 0,
            "servo_locked": servo_locked
        }
        try:
            response = requests.post(f"{SERVER_URL}/flet/update", json=data)
            if response.status_code != 200:
                print("Error sending data to server")
        except requests.RequestException as e:
            print(f"Network error: {e}")

    def update_table():
        timestamp = datetime.now().strftime("%H:%M:%S")
        sensor_history.append({
            "timestamp": timestamp,
            "potentiometer": analog_input,
            "motion": motion_detected
        })

        if len(sensor_history) > 10:
            sensor_history.pop(0)

        sensor_table.rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(entry["timestamp"])),
                    ft.DataCell(ft.Text(str(entry["potentiometer"]))),
                    ft.DataCell(ft.Text("Detected" if entry["motion"] else "Not Detected")),
                ]
            ) for entry in sensor_history
        ]
        page.update()

    def update_dashboard():
        nonlocal analog_input, button_pressed, motion_detected, led_state, is_manual_override, last_override_value
        last_table_update = time.time()
        while True:
            try:
                response = requests.get(f"{SERVER_URL}/dashboard")
                if response.status_code == 200:
                    data = response.json()

                    # Update sensor values
                    raw_value = data["esp"]["analog_input"]
                    new_analog_input = int((raw_value / 4095) * 49) + 1
                    button_pressed = data["esp"]["button"]
                    motion_detected = data["esp"]["motion"]

                    # Check if potentiometer changed significantly (threshold = 3)
                    if is_manual_override and abs(new_analog_input - last_override_value) >= 3:
                        is_manual_override = False  # Return to auto-control

                    # Update LED state only if not in manual override
                    if not is_manual_override:
                        new_led_state = new_analog_input < 25
                        if new_led_state != led_state:
                            led_state = new_led_state
                            led_button.text = f"Turn LED {'OFF' if led_state else 'ON'}"
                            send_flet_data()

                    # Update displays
                    analog_input = new_analog_input
                    analog_display.value = f"Potentiometer: {analog_input}"
                    button_display.value = f"Button: {'Pressed' if button_pressed else 'Not Pressed'}"
                    motion_display.value = f"Motion: {'Detected' if motion_detected else 'Not Detected'}"
                    motion_indicator.bgcolor = ft.colors.RED if motion_detected else ft.colors.RED_200

                    # Update table periodically
                    if time.time() - last_table_update >= TABLE_UPDATE_INTERVAL:
                        update_table()
                        last_table_update = time.time()

                    page.update()
            except requests.RequestException as e:
                print(f"Dashboard update error: {e}")
            time.sleep(UPDATE_INTERVAL)

    # Add the scrollable content to the page
    page.add(main_content)

    # Start background thread for dashboard updates
    threading.Thread(target=update_dashboard, daemon=True).start()


ft.app(target=main)