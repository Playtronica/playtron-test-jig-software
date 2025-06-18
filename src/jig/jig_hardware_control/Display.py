from .I2CLCD import I2CLCD
from .rgb_led import RgbLed

import variables
from base_logger import get_logger_for_file

logger = get_logger_for_file(__name__)


class Display:
    _instance = None

    def __init__(self):
        self.screen = I2CLCD(address=variables.SCREEN_ADDRESS,
                             cols=variables.SCREEN_COLUMNS,
                             rows=variables.SCREEN_ROWS)
        self.rgb_led = RgbLed()
        self.device_count = 0

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_text(self, text):
        if not self.__validate_text_for_screen(text):
            logger.warning("Some problems with text")
            return False

        self.screen.clear()

        self.screen.set_cursor(0, 0)
        self.screen.write(text)
        self.screen.set_cursor(0, 1)
        self.screen.write(variables.JIG_FIRMWARE_VERSION)
        self.screen.set_cursor(4, 1)
        self.screen.write(variables.BIOTRON_FIRMWARE_VERSION)
        self.screen.set_cursor(variables.SCREEN_COLUMNS - 4, 1)
        self.screen.write(f"{self.device_count:04}")

    def set_color(self, color):
        self.rgb_led.set_color(color)

    def __validate_text_for_screen(self, text):
        if len(text) > variables.SCREEN_COLUMNS:
            logger.warn("Text is too long")
            return False

        return True

