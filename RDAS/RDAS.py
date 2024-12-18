import serial
import pynmea2
import gspread
import os
import time
import subprocess
import smbus

# Define some device parameters
I2C_ADDR  = 0x27  # I2C device address
LCD_WIDTH = 16    # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT  = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Open I2C interface
bus = smbus.SMBus(0)  # Change to bus 0 for /dev/i2c-0

# Define the GPIO pin number (BCM numbering)
gpio_pin = 79 

# Paths to the sysfs files
gpio_path = f"/sys/class/gpio/gpio{gpio_pin}/"
export_path = "/sys/class/gpio/export"
unexport_path = "/sys/class/gpio/unexport"
direction_path = os.path.join(gpio_path, "direction")
value_path = os.path.join(gpio_path, "value")  


# Function to export the GPIO pin
def export_gpio(pin):
    if not os.path.exists(gpio_path):
        try:
            with open(export_path, 'w') as f:
                f.write(str(pin))
        except IOError as e:
            print(f"Error exporting GPIO pin: {e}")

# Function to unexport the GPIO pin
def unexport_gpio(pin):
    if os.path.exists(gpio_path):
        try:
            with open(unexport_path, 'w') as f:
                f.write(str(pin))
        except IOError as e:
            print(f"Error unexporting GPIO pin: {e}")

# Function to set the direction of the GPIO pin
def set_direction(direction):
    try:
        with open(direction_path, 'w') as f:
            f.write(direction)
    except IOError as e:
        print(f"Error setting GPIO direction: {e}")

# Function to read the value from the GPIO pin
def read_value():
    try:
        with open(value_path, 'r') as f:
            return f.read().strip()
    except IOError as e:
        print(f"Error reading GPIO value: {e}")
        return None

# Function to write a value to the GPIO pin
def write_value(value):
    command = f"echo {value} > {value_path}"
    subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
    lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
    lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
    lcd_byte(0x0C, LCD_CMD)  # 001100 Display On, Cursor Off, Blink Off 
    lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
    lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
    bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

    # High bits
    bus.write_byte(I2C_ADDR, bits_high)
    lcd_toggle_enable(bits_high)

    # Low bits
    bus.write_byte(I2C_ADDR, bits_low)
    lcd_toggle_enable(bits_low)

def lcd_toggle_enable(bits):
    time.sleep(E_DELAY)
    bus.write_byte(I2C_ADDR, (bits | ENABLE))
    time.sleep(E_PULSE)
    bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
    time.sleep(E_DELAY)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

def main():
    com_port = "/dev/ttyUSB0"
    lcd_init()
    export_gpio(gpio_pin)
    
    try:
        ser = serial.Serial(com_port, 9600, timeout=5)
        print(f"Opened COM port {com_port}")
        
        while True:
            acknowledgment_status = False
            lcd_string("   DRIVER IS ", LCD_LINE_1)
            lcd_string("    MISSING  ", LCD_LINE_2)
       
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
            set_direction("out")
            write_value(1)
            set_direction("in")
            value = read_value()
            if value == "0":
                acknowledgment_status = True
                print(f"Acknowledgment button status: {acknowledgment_status}")
            else:
                print(f"Acknowledgment button status: {acknowledgment_status}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting gracefully")
    
    finally:
        unexport_gpio(gpio_pin)

if __name__ == "__main__":
    main()

