import os
import time
import subprocess
import smbus

# Define some device parameters
I2C_ADDR = 0x27  # I2C device address
LCD_WIDTH = 16  # Maximum characters per line

# Define some device constants
LCD_CHR = 1  # Mode - Sending data
LCD_CMD = 0  # Mode - Sending command

LCD_LINE_1 = 0x80  # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0  # LCD RAM address for the 2nd line

LCD_BACKLIGHT = 0x08  # On
ENABLE = 0b00000100  # Enable bit

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

# Define the GPIO pin number (BCM numbering)
gpio_pin = 79

# Paths to the sysfs files
gpio_path = f"/sys/class/gpio/gpio{gpio_pin}/"
export_path = "/sys/class/gpio/export"
unexport_path = "/sys/class/gpio/unexport"
direction_path = os.path.join(gpio_path, "direction")
value_path = os.path.join(gpio_path, "value")


class DeviceInterface:
    def __init__(self):
        self.bus = smbus.SMBus(0)  # Change to bus 0 for /dev/i2c-0

    def export_gpio(self):
        if not os.path.exists(gpio_path):
            try:
                with open(export_path, 'w') as f:
                    f.write(str(gpio_pin))
            except IOError as e:
                print(f"Error exporting GPIO pin: {e}")

    def unexport_gpio(self):
        if os.path.exists(gpio_path):
            try:
                with open(unexport_path, 'w') as f:
                    f.write(str(gpio_pin))
            except IOError as e:
                print(f"Error unexporting GPIO pin: {e}")

    def set_direction(self, direction):
        try:
            with open(direction_path, 'w') as f:
                f.write(direction)
        except IOError as e:
            print(f"Error setting GPIO direction: {e}")

    def read_value(self):
        try:
            with open(value_path, 'r') as f:
                return f.read().strip()
        except IOError as e:
            print(f"Error reading GPIO value: {e}")
            return None

    def write_value(self, value):
        command = f"echo {value} > {value_path}"
        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def lcd_init(self):
        self.lcd_byte(0x33, LCD_CMD)  # 110011 Initialise
        self.lcd_byte(0x32, LCD_CMD)  # 110010 Initialise
        self.lcd_byte(0x06, LCD_CMD)  # 000110 Cursor move direction
        self.lcd_byte(0x0C, LCD_CMD)  # 001100 Display On, Cursor Off, Blink Off
        self.lcd_byte(0x28, LCD_CMD)  # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, LCD_CMD)  # 000001 Clear display
        time.sleep(E_DELAY)

    def lcd_byte(self, bits, mode):
        bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT
        bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT

        # High bits
        self.bus.write_byte(I2C_ADDR, bits_high)
        self.lcd_toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(I2C_ADDR, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        time.sleep(E_DELAY)
        self.bus.write_byte(I2C_ADDR, (bits | ENABLE))
        time.sleep(E_PULSE)
        self.bus.write_byte(I2C_ADDR, (bits & ~ENABLE))
        time.sleep(E_DELAY)

    def lcd_string(self, message, line):
        message = message.ljust(LCD_WIDTH, " ")
        self.lcd_byte(line, LCD_CMD)

        for i in range(LCD_WIDTH):
            self.lcd_byte(ord(message[i]), LCD_CHR)
