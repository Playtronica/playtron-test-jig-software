import time

from .pin_controller import PinController
from .ads1015 import ADS1015


class MultiplexerADCReader:
    _instance = None
    def __init__(self):
        self.pin_controller = PinController()
        self.adc = ADS1015()

        # Multiplexer control pins (connected to GPIO via PinController)
        self.S0 = 1  # GP1
        self.S1 = 2  # GP2
        self.S2 = 3  # GP3
        self.E1 = 4  # GP4 (enable for first multiplexer)
        self.E2 = 5  # GP5 (enable for second multiplexer)

        # Set up GPIO directions
        self._initialize_gpio()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize_gpio(self):
        """Initialize GPIO pins for controlling multiplexers."""
        for pin in [self.S0, self.S1, self.S2, self.E1, self.E2]:
            self.pin_controller.gpio_set_pin_direction(pin, 0)  # Set as output

        # Disable both multiplexers initially
        self.pin_controller.gpio_write_pin(self.E1, 1)
        self.pin_controller.gpio_write_pin(self.E2, 1)

    def _set_channel(self, channel):
        """Set the multiplexer channel (0-7)."""
        if not (0 <= channel <= 7):
            raise ValueError("Channel must be between 0 and 7.")

        # Set S0, S1, S2 based on the channel number
        self.pin_controller.gpio_write_pin(self.S0, (channel >> 0) & 1)
        self.pin_controller.gpio_write_pin(self.S1, (channel >> 1) & 1)
        self.pin_controller.gpio_write_pin(self.S2, (channel >> 2) & 1)

    def read_channel(self, multiplexer, channel):
        """Read an analog value from a specific channel of a multiplexer.

        Args:
            multiplexer (int): The multiplexer number (0 or 1).
            channel (int): The channel number (0-7).

        Returns:
            float: The analog value in volts.
        """
        if multiplexer not in [0, 1]:
            raise ValueError("Multiplexer must be 1 or 2.")

        # Enable the selected multiplexer
        if multiplexer == 0:
            self.pin_controller.gpio_write_pin(self.E1, 0)  # Enable first multiplexer
            self.pin_controller.gpio_write_pin(self.E2, 1)  # Disable second multiplexer
        else:
            self.pin_controller.gpio_write_pin(self.E1, 1)  # Disable first multiplexer
            self.pin_controller.gpio_write_pin(self.E2, 0)  # Enable second multiplexer

        # Set the channel on the multiplexer
        self._set_channel(channel)

        # Read from ADC channel 0
        value = self.adc.read_single_channel(0)

        # Disable both multiplexers after reading
        self.pin_controller.gpio_write_pin(self.E1, 1)
        self.pin_controller.gpio_write_pin(self.E2, 1)

        return value


