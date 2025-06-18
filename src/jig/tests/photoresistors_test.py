import time

import variables
from jig.jig_hardware_control.pin_controller import PinController
from .serial_tests import SerialTests
from base_logger import get_logger_for_file

serial = SerialTests()
pin_controller = PinController()
logger = get_logger_for_file(__name__)


def get_photoresistors_state():
    res = 0
    for _ in range(variables.PHOTORESISTOR_SAMPLES):
        data = serial.last_data.copy()
        if "photoresistor_adc" not in data:
            logger.warning("Photo resistors data missing")
            return -1
        res += data["photoresistor_adc"]
        time.sleep(0.1)

    return res / variables.PHOTORESISTOR_SAMPLES


def photoresistors_test():
    no_led_photoresistors_state = get_photoresistors_state()
    if no_led_photoresistors_state == -1:
        logger.warn("Some problems with getting status")
        return "GET_DATA_FAILED"

    logger.info(f"Photoresistor state without leds: {no_led_photoresistors_state}")

    pin_controller.gpio_write_pin(6, 1)
    led_photoresistors_state = get_photoresistors_state()
    pin_controller.gpio_write_pin(6, 0)

    if no_led_photoresistors_state == -1:
        logger.warn("Some problems with getting status")
        return "GET_DATA_FAILED"

    logger.info(f"Photo resistors state with leds: {led_photoresistors_state}")

    if no_led_photoresistors_state - led_photoresistors_state < 100:
        logger.warn("Photoresistor test failed")
        return "TEST_FAILED"

    logger.info("Photoresistor test complete successfully")
    return
