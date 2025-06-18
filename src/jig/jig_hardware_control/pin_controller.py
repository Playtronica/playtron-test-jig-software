import gpiozero
from gpiozero import Button
import time
from .tca9535 import TCA9535

from base_logger import get_logger_for_file
logger = get_logger_for_file(__name__)

class PinController:
    _instance = None
    def __init__(self):
        # Initialize the TCA9535 expander
        self.tca9535 = TCA9535()

        # # Define the interrupt pin (using BCM numbering, pin 4 as example for INT)
        # self.INT_PIN = 4

        # # Check if the interrupt_pin already exists and free it if needed
        # if hasattr(self, 'interrupt_pin') and self.interrupt_pin is not None:
        #     try:
        #         self.interrupt_pin.close()
        #         print(f"GPIO{self.INT_PIN} (interrupt pin) released.")
        #     except Exception as e:
        #         print(f"Failed to release GPIO{self.INT_PIN}: {e}")

        # # Initialize the interrupt pin only if it hasn't been initialized
        # try:
        #     self.interrupt_pin = Button(self.INT_PIN, pull_up=True, bounce_time=0.2)  # 200 ms debounce
        #     print("Interrupt pin initialized with debounce protection.")
        # except gpiozero.exc.GPIOPinInUse:
        #     print(f"GPIO{self.INT_PIN} is already in use by another process. Skipping initialization.")
        #     self.interrupt_pin = None  # Ensure it's set to None if not initialized

        # # Register the interrupt callback function for handling falling edges only if initialization succeeded
        # if self.interrupt_pin is not None and self.interrupt_pin.when_pressed is None:
        #     self.interrupt_pin.when_pressed = self._handle_interrupt

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # def _handle_interrupt(self):
    #     """
    #     Internal method to handle the GPIO interrupt.
    #     Called when a falling edge is detected on the INT_PIN.
    #     """
    #     print(f"Interrupt detected on GPIO {self.INT_PIN}")

    #     # Call the user's custom interrupt handler if set
    #     if self.user_interrupt_handler:
    #         self.user_interrupt_handler()

    # def set_interrupt_handler(self, handler):
    #     """
    #     Allows the user to set a custom interrupt handler.
    #     """
    #     self.user_interrupt_handler = handler

    def gpio_set_pin_direction(self, pin, direction):
        """
        Sets the direction for a specific pin on port 0.
        
        pin: Pin number (0-7).
        direction: Direction (1 - input, 0 - output).
        """
        current_config = self.tca9535.read_register(0x06)  # Configuration register for port 0
        if direction:
            current_config |= (1 << pin)  # Set bit for input
        else:
            current_config &= ~(1 << pin)  # Clear bit for output
        self.tca9535.write_register(0x06, current_config)

    def gpio_write_pin(self, pin, value):
        """
        Writes a value to a specific pin on port 0.
        
        pin: Pin number (0-7).
        value: State (1 - high, 0 - low).
        """
        self.tca9535.set_pin(0, pin, value)

    def gpio_read_pin(self, pin):
        """
        Reads the state of a specific pin on port 0.
        
        pin: Pin number (0-7).
        """
        current_state = self.tca9535.read_register(0x00)  # Input register for port 0
        return (current_state >> pin) & 1

    def gpio_set_port_direction(self, direction_byte):
        """
        Sets the direction for all pins on port 0 (group operation).
        
        direction_byte: Byte where each bit represents the direction for a pin (1 - input, 0 - output).
        """
        self.tca9535.write_register(0x06, direction_byte)

    def gpio_write_port(self, value_byte):
        """
        Writes a byte to port 0 (group operation).
        
        value_byte: Byte to write, where each bit represents the state of a pin (1 - high, 0 - low).
        """
        self.tca9535.write_register(0x02, value_byte)

    def gpio_read_port(self):
        """
        Reads the state of all pins on port 0 (group operation).
        
        Returns a byte where each bit represents the state of a pin.
        """
        return self.tca9535.read_register(0x00)

    # Relay control using TCA9535
    def relay_set(self, relay_number, state, delay=0):
        """
        Controls relays by switching pins 0-3 of port 1 on the TCA9535.
        
        relay_number: Relay number from 1 to 4 (1 corresponds to pin 0).
        state: State (1 - on, 0 - off).
        delay: Optional delay in seconds after switching the relay.
        
        Returns:
            1 - Success.
            0 - Error (if relay_number is out of bounds).
        """
        try:
            if 1 <= relay_number <= 4:
                pin = relay_number - 1  # Convert 1-4 to 0-3
                self.tca9535.set_pin(1, pin, not state)
                logger.debug(f"Relay {relay_number}: {'ON' if state else 'OFF'}, pin {pin}")

                # Выполняем задержку, если она указана
                if delay > 0:
                    time.sleep(delay)
                return 1  # Success
            else:
                logger.warn("Error: Relay number must be between 1 and 4.")
                return 0  # Error
        except Exception as e:
            logger.debug(f"Error while setting relay: {e}")
            return 0  # Error
                
    def usb_power_set(self, usb_port_number, state):
        """
        Controls USB power by switching pins 4-7 of port 1 on the TCA9535.
        
        usb_port_number: USB port number from 1 to 4 (1 corresponds to pin 4, 4 to pin 7).
        state: State (1 - on, 0 - off).
        """
        try:
            if 1 <= usb_port_number <= 4:
                pin = usb_port_number + 3  # Convert 1-4 to 4-7
                self.tca9535.set_pin(1, pin, not state)
                logger.debug(f"USB port {usb_port_number}: {'ON' if state else 'OFF'}, pin {pin}")
                return 1  # Успешное выполнение
            else:
                raise ValueError("USB port number must be between 1 and 4.")
        except Exception as e:
            logger.debug(f"Error setting USB power: {e}")
            return 0  # Ошибка выполнения
        
    def cleanup(self):
        """
        Cleans up the GPIO resources and releases the handle.
        """
        # Set all relays OFF and all USB ports ON before cleanup
        for i in range(1, 5):
            self.relay_set(i, 0)  # Set all relays OFF
            self.usb_power_set(i, 1)  # Set all USB ports ON

        # Close the Button object to free GPIO4 if it exists
        if hasattr(self, 'interrupt_pin') and self.interrupt_pin is not None:
            try:
                self.interrupt_pin.close()
                logger.debug(f"GPIO{self.INT_PIN} (interrupt pin) released.")
            except Exception as e:
                logger.debug(f"Failed to release GPIO{self.INT_PIN}: {e}")

        logger.debug("GPIO resources cleaned up.")