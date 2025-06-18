import smbus2
import time

# Constants for LCD commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# Flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# Flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# Flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# Flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

# Flags for backlight control
LCD_BACKLIGHT = 0x08
LCD_NOBACKLIGHT = 0x00

# Control bits
En = 0b00000100  # Enable bit
Rw = 0b00000010  # Read/Write bit
Rs = 0b00000001  # Register select bit

class I2CLCD:
    _instance = None

    def __init__(self, address, cols, rows, bus=1):
        self.bus = smbus2.SMBus(bus)
        self.address = address
        self.cols = cols
        self.rows = rows
        self.backlightval = LCD_BACKLIGHT
        self.displayfunction = LCD_4BITMODE | LCD_1LINE | LCD_5x8DOTS
        self.displaycontrol = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF
        self.displaymode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
        self.init_lcd()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def write_command(self, cmd):
        """Send command to the LCD."""
        self.send(cmd, 0)

    def write_data(self, data):
        """Send data to the LCD."""
        self.send(data, Rs)

    def send(self, data, mode):
        """Send data or command."""
        high_nibble = mode | (data & 0xF0) | self.backlightval
        low_nibble = mode | ((data << 4) & 0xF0) | self.backlightval
        self.expander_write(high_nibble)
        self.pulse_enable(high_nibble)
        self.expander_write(low_nibble)
        self.pulse_enable(low_nibble)
        
    def write(self, text):
        """Write a string to the display."""
        for char in text:
            self.write_data(ord(char))

    def expander_write(self, data):
        """Write data to the I2C expander."""
        self.bus.write_byte(self.address, data)

    def pulse_enable(self, data):
        """Pulse the enable pin."""
        self.expander_write(data | En)
        time.sleep(0.0001)
        self.expander_write(data & ~En)
        time.sleep(0.0001)

    def clear(self):
        """Clear the display."""
        self.write_command(LCD_CLEARDISPLAY)
        time.sleep(0.002)

    def home(self):
        """Return cursor to home position."""
        self.write_command(LCD_RETURNHOME)
        time.sleep(0.002)

    def set_cursor(self, col, row):
        """Set the cursor position."""
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.rows:
            row = self.rows - 1
        self.write_command(LCD_SETDDRAMADDR | (col + row_offsets[row]))

    def display(self):
        """Turn on the display."""
        self.displaycontrol |= LCD_DISPLAYON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def no_display(self):
        """Turn off the display."""
        self.displaycontrol &= ~LCD_DISPLAYON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self):
        """Turn on the cursor."""
        self.displaycontrol |= LCD_CURSORON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def no_cursor(self):
        """Turn off the cursor."""
        self.displaycontrol &= ~LCD_CURSORON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink(self):
        """Turn on blinking cursor."""
        self.displaycontrol |= LCD_BLINKON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def no_blink(self):
        """Turn off blinking cursor."""
        self.displaycontrol &= ~LCD_BLINKON
        self.write_command(LCD_DISPLAYCONTROL | self.displaycontrol)

    def scroll_display_left(self):
        """Scroll the display to the left."""
        self.write_command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

    def scroll_display_right(self):
        """Scroll the display to the right."""
        self.write_command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

    def left_to_right(self):
        """Set text direction left to right."""
        self.displaymode |= LCD_ENTRYLEFT
        self.write_command(LCD_ENTRYMODESET | self.displaymode)

    def right_to_left(self):
        """Set text direction right to left."""
        self.displaymode &= ~LCD_ENTRYLEFT
        self.write_command(LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
        """Enable autoscroll."""
        self.displaymode |= LCD_ENTRYSHIFTINCREMENT
        self.write_command(LCD_ENTRYMODESET | self.displaymode)

    def no_autoscroll(self):
        """Disable autoscroll."""
        self.displaymode &= ~LCD_ENTRYSHIFTINCREMENT
        self.write_command(LCD_ENTRYMODESET | self.displaymode)

    def backlight(self):
        """Turn on backlight."""
        self.backlightval = LCD_BACKLIGHT
        self.expander_write(0)

    def no_backlight(self):
        """Turn off backlight."""
        self.backlightval = LCD_NOBACKLIGHT
        self.expander_write(0)

    def create_char(self, location, charmap):
        """Create a custom character."""
        location &= 0x7
        self.write_command(LCD_SETCGRAMADDR | (location << 3))
        for char in charmap:
            self.write_data(char)

    def init_lcd(self):
        """Initialize the LCD."""
        time.sleep(0.05)  # Wait for LCD to boot
        self.expander_write(self.backlightval)
        time.sleep(0.01)

        # Send initialization sequence
        self.write_command(0x03)
        time.sleep(0.005)
        self.write_command(0x03)
        time.sleep(0.005)
        self.write_command(0x03)
        time.sleep(0.005)
        self.write_command(0x02)

        # Set function
        self.write_command(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS)
        self.display()
        self.clear()
        self.write_command(LCD_ENTRYMODESET | self.displaymode)


# Example usage
if __name__ == "__main__":
    lcd = I2CLCD(address=0x27, cols=16, rows=2)
    lcd.clear()
    lcd.set_cursor(0, 0)
    lcd.write("Test in progress")
    lcd.set_cursor(0, 1)
    lcd.write("01 BOOT MODE")
