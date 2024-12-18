

# GPS Interaction and Device Interface Library

This repository contains two Python scripts that enable interaction with hardware components such as a GPS module, an I2C-connected LCD display, and GPIO pins on a Linux-based system. The scripts included are:

1. **`main.py`** - Facilitates communication with a GPS module to process NMEA data, and uses an LCD display and GPIO interface for real-time status updates.
2. **`device_interface.py`** - Defines the `DeviceInterface` class, providing essential methods for managing I2C-connected LCD displays and GPIO pins.

## Prerequisites

Before running these scripts, ensure your environment meets the following requirements:

- **Python 3.x**
- **Required Python libraries:** `pynmea2`, `smbus`
- **Hardware components:** GPS module, LCD display connected via I2C, GPIO pins
- **Operating system:** Linux-based system with enabled support for I2C and GPIO operations

## Installation

1. **Install the required Python libraries:**

   ```bash
   pip install pynmea2 smbus
   ```

2. **Enable I2C and GPIO** on your Linux system, depending on your hardware configuration.

## Usage

### `main.py`

This script interfaces with a GPS module connected via a serial port, processes incoming NMEA sentences, and utilizes a GPIO pin for user acknowledgment. It also displays status messages on an LCD screen.

**To execute the script:**

```bash
python3 main.py
```

**Core functionalities include:**
- **GPS Data Acquisition:** Connects to a GPS module on `/dev/ttyUSB0`, reads NMEA sentences, and extracts GPS data (latitude, longitude, speed).
- **LCD Display Management:** Displays real-time messages on an LCD screen, indicating the status of the driver.
- **GPIO Interaction:** Monitors a GPIO pin to check if an acknowledgment button has been pressed.

### `device_interface.py`

The `device_interface.py` script defines the `DeviceInterface` class, which provides a robust interface for managing I2C-connected LCD displays and GPIO pins. Below is a detailed overview of the methods within this class and their respective uses in `main.py`:

#### 1. **`__init__(self)`**

- **Purpose:** Initializes the I2C bus connection necessary for communication with the LCD display.
- **Usage in `main.py`:** Automatically invoked upon creating an instance of `DeviceInterface`.

```python
device = DeviceInterface()
```

#### 2. **`export_gpio(self)`**

- **Purpose:** Exports the specified GPIO pin, making it accessible via the `/sys/class/gpio/` interface for subsequent read/write operations.
- **Usage in `main.py`:** Called during initialization to prepare the GPIO pin for use.

```python
device.export_gpio()
```

#### 3. **`unexport_gpio(self)`**

- **Purpose:** Unexports the GPIO pin, effectively releasing it and cleaning up resources when the script terminates.
- **Usage in `main.py`:** Called in the `finally` block to ensure the GPIO pin is unexported when the script ends, either normally or due to an interruption.

```python
device.unexport_gpio()
```

#### 4. **`set_direction(self, direction)`**

- **Purpose:** Configures the GPIO pin's direction as either input (`in`) or output (`out`).
- **Usage in `main.py`:** The GPIO pin's direction is set before performing read or write operations.

```python
device.set_direction("out")
device.set_direction("in")
```

#### 5. **`write_value(self, value)`**

- **Purpose:** Writes a specified value (`1` or `0`) to the GPIO pin, which can be used to trigger external hardware actions.
- **Usage in `main.py`:** Writes a value of `1` to the GPIO pin as part of the interaction with connected hardware.

```python
device.write_value(1)
```

#### 6. **`read_value(self)`**

- **Purpose:** Reads the current value from the GPIO pin, typically used to detect the status of a button press or similar input.
- **Usage in `main.py`:** Reads the GPIO pin value to determine whether the acknowledgment button has been pressed.

```python
value = device.read_value()
```

#### 7. **`lcd_init(self)`**

- **Purpose:** Initializes the LCD display by sending a series of configuration commands, such as clearing the display and setting the cursor position.
- **Usage in `main.py`:** Called during initialization to prepare the LCD display for subsequent use.

```python
device.lcd_init()
```

#### 8. **`lcd_byte(self, bits, mode)`**

- **Purpose:** Sends a byte of data or a command to the LCD. The `mode` parameter dictates whether the byte is interpreted as a command (`LCD_CMD`) or data (`LCD_CHR`).
- **Usage:** This method is used internally by other methods such as `lcd_init` and `lcd_string`. Direct invocation in `main.py` is not required.

#### 9. **`lcd_toggle_enable(self, bits)`**

- **Purpose:** Toggles the enable bit on the LCD to latch data or commands. This is part of the low-level communication process with the LCD.
- **Usage:** This method is used internally by `lcd_byte` and is not called directly in `main.py`.

#### 10. **`lcd_string(self, message, line)`**

- **Purpose:** Displays a string of text on a specified line of the LCD. The message is automatically padded or truncated to fit the LCD's width.
- **Usage in `main.py`:** Displays messages such as `"DRIVER IS MISSING"` on the LCD.

```python
device.lcd_string("   DRIVER IS ", device.LCD_LINE_1)
device.lcd_string("    MISSING  ", device.LCD_LINE_2)
```

### Methodology in `main.py`

- The script initializes an instance of `DeviceInterface`, which sets up the I2C connection and prepares the LCD display.
- `lcd_init()` configures the LCD display for use.
- `export_gpio()` prepares the GPIO pin for interaction.
- In the primary loop, GPS data is continuously read and displayed on the LCD, while the GPIO pin is monitored for user acknowledgment.
- Upon termination, `unexport_gpio()` ensures proper cleanup of the GPIO resources.

## Hardware Configuration

1. **GPS Module:** Connect the GPS module to the appropriate serial port (e.g., `/dev/ttyUSB0`).
2. **I2C LCD Display:** Connect the LCD display to the I2C bus (default address `0x27`).
3. **GPIO Pin:** Ensure the GPIO pin is properly connected to an acknowledgment button or another suitable input device.

## Additional Notes

- Verify that the correct I2C bus is selected (`bus 0` is the default in `device_interface.py`). Adjust this setting if necessary for your hardware.
- Modify the `com_port` variable in `main.py` if your GPS module is connected to a different serial port.
- The default GPIO pin is `79`, which may need to be altered based on your specific hardware setup.



This `README.md` is designed to provide clear, professional guidance for understanding and using the provided scripts. It includes detailed explanations of all methods within the `DeviceInterface` class and their implementation within the `main.py` script.