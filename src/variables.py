import os
from pathlib import Path

JIG_FIRMWARE_VERSION = 'A01'
DEVICE_FIRMWARE_VERSION = "0.00.00"


ROOT_PATH = Path(__file__).parent.parent
FIRMWARE_PATH = ROOT_PATH / "firmware"
os.makedirs(FIRMWARE_PATH, exist_ok=True)

LOGGER_PATH = ROOT_PATH / "logs"
os.makedirs(LOGGER_PATH, exist_ok=True)

MAX_TEST_TIME = 70

MOUNT_POINT = Path("/media/usb")
FIRMWARE_PATTERN = r"playtron-firmware_v\d+\.\d+\.\d+\.uf2"

SCREEN_ADDRESS = 0x27
SCREEN_ROWS = 2
SCREEN_COLUMNS = 16

RGB_LED_RED_PIN = 5
RGB_LED_GREEN_PIN = 6
RGB_LED_BLUE_PIN = 13
RGB_LED_CHIP_NAME = "/dev/gpiochip0"

PHOTORESISTOR_SAMPLES = 5

PlANTS_SAMPLES = 5

LED_TEST_BLUE_LEDS_MIN_REQ = 3.2
LED_TEST_GREEN_LEDS_MIN_REQ = 2.7
