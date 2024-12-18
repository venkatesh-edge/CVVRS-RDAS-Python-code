import serial
import pynmea2
import time
from device_interface import DeviceInterface


def main():
    com_port = "/dev/ttyUSB0"
    device = DeviceInterface()
    device.lcd_init()
    device.export_gpio()

    try:
        ser = serial.Serial(com_port, 9600, timeout=5)
        print(f"Opened COM port {com_port}")

        while True:
            acknowledgment_status = False
            device.lcd_string("   DRIVER IS ", device.LCD_LINE_1)
            device.lcd_string("    MISSING  ", device.LCD_LINE_2)

            try:
                data = ser.readline().decode('ascii', errors='replace')

                if data.startswith("$GPRMC"):
                    try:
                        msg = pynmea2.parse(data)
                        latitude = msg.latitude
                        longitude = msg.longitude
                        speed = msg.spd_over_grnd
                        print(f"Latitude: {latitude}, Longitude: {longitude}, Speed (knots): {speed}")

                        # Optional: Add code to save to Google Sheets here

                    except pynmea2.ParseError as e:
                        print(f"Parse error: {e}")

            except Exception as e:
                print(f"Error reading data: {e}")

            # GPIO Interaction
            device.set_direction("out")
            device.write_value(1)
            device.set_direction("in")
            value = device.read_value()
            if value == "0":
                acknowledgment_status = True
                print(f"Acknowledgment button status: {acknowledgment_status}")
            else:
                print(f"Acknowledgment button status: {acknowledgment_status}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting gracefully")

    finally:
        device.unexport_gpio()


if __name__ == "__main__":
    main()
