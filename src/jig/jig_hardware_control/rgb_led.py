import gpiod
import enum
import variables

class RgbColorsEnum(enum.Enum):
    NONE = (0, 0, 0)
    RED = (1, 0, 0)
    GREEN = (0, 1, 0)
    BLUE = (0, 0, 1)
    YELLOW = (1, 1, 0)
    PURPLE = (1, 0, 1)
    LIGHT_BLUE = (0, 1, 1)
    WHITE = (1, 1, 1)

class RgbLed:
    _instance = None

    def __init__(self):
        self.chip = gpiod.Chip(variables.RGB_LED_CHIP_NAME)
        self.lines = self.chip.get_lines([variables.RGB_LED_RED_PIN, variables.RGB_LED_GREEN_PIN, variables.RGB_LED_BLUE_PIN])
        self.lines.request(consumer="rgb_control", type=gpiod.LINE_REQ_DIR_OUT)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set_color(self, color):
        if type(color) is RgbColorsEnum:
            color = color.value

        self.lines.set_values([1 - color[0], 1 - color[1], 1 - color[2]])

