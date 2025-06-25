import logging
import time

from base_logger import get_logger_for_file
from .pin_controller import PinController
from .ads1015 import ADS1015

logger = get_logger_for_file(__name__)

class MultiplexerADCReader:
    _instance = None
    def __init__(self):
        self.pin_controller = PinController()
        self.adc = ADS1015()

        self.channel_controller_gpio = (1, 2)
        self.multiplexer_gpio = (3, 4, 5, 6)

        # Set up GPIO directions
        self._initialize_gpio()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _initialize_gpio(self):
        """Initialize GPIO pins for controlling multiplexers."""
        for pin in self.channel_controller_gpio + self.multiplexer_gpio:
            self.pin_controller.gpio_set_pin_direction(pin, 0)  # Set as output

        # Disable all multiplexers initially
        self._set_multiplexer(None)
    def _set_channel(self, channel):
        """Set the multiplexer channel (0-3)."""
        if not (0 <= channel <= 3):
            raise ValueError("Channel must be between 0 and 3.")

        # Set S0, S1 based on the channel number
        logger.debug("Start channel set")
        for i in range(len(self.channel_controller_gpio)):
            self.pin_controller.gpio_write_pin(self.channel_controller_gpio[i], (channel >> i) & 1)
            logger.debug((channel >> i) & 1)
        logger.debug("End channel set")

    def _set_multiplexer(self, multiplexer):
        if not (multiplexer is None or 0 <= multiplexer <= 3):
            raise ValueError("Multiplexer must be between 0 and 3.")

        logger.debug("Start multiplexer set")
        for i in range(len(self.multiplexer_gpio)):
            self.pin_controller.gpio_write_pin(self.multiplexer_gpio[i], 1 if i != multiplexer else 0)
            logger.debug(1 if i != multiplexer else 0)
        logger.debug("End multiplexer set")

    def read_channel(self, multiplexer, channel):
        """Read an analog value from a specific channel of a multiplexer.

        Args:
            multiplexer (int): The multiplexer number (0 or 1).
            channel (int): The channel number (0-7).

        Returns:
            float: The analog value in volts.
        """
        self._set_multiplexer(multiplexer)

        # Set the channel on the multiplexer
        self._set_channel(channel)
        time.sleep(0.02)

        # Read from ADC channel 0
        value = self.adc.read_single_channel(0)
        time.sleep(0.02)

        # Disable both multiplexers after reading
        self._set_multiplexer(None)
        time.sleep(0.02)

        return value


