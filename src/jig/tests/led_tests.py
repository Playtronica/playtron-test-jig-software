import time

import variables
from base_logger import get_logger_for_file
from jig.jig_hardware_control.ads1015_4051 import MultiplexerADCReader
from jig.tests.midi_processes import send_test_green_sysex_messages_to_midi_device, \
    send_test_blue_sysex_messages_to_midi_device

logger = get_logger_for_file(__name__)


adc_read = MultiplexerADCReader()




def led_tests(data):
    for multiplexer_num in range(2):
        for multiplexer_channel_num in range(8):
            adc_val = adc_read.read_channel(multiplexer_num, multiplexer_channel_num)
            logger.info(f"Value of multiplexer {multiplexer_num} {multiplexer_channel_num}: {adc_val}")
            adc_val -= 0.05

            if adc_val >= data[(multiplexer_num, multiplexer_channel_num)]:
                logger.warn(f"Problems with blue led {multiplexer_num} {multiplexer_channel_num}: {adc_val}")
                return "LED_TEST_FAILED"

            time.sleep(0.1)

    return


def check_blue_led():
    logger.info("Checking blue LED")
    send_test_blue_sysex_messages_to_midi_device()
    data = {
        (0, 0): 3.211666666666667, (0, 1): 3.211666666666667, (0, 2): 3.211666666666667,
        (0, 3): 3.2195, (0, 4): 3.2195, (0, 5): 3.2195, (0, 6): 3.2508333333333335,
        (0, 7): 3.2508333333333335, (1, 0): 3.2508333333333335, (1, 1): 3.2508333333333335,
        (1, 2): 3.2508333333333335, (1, 3): 3.2508333333333335, (1, 4): 3.2508333333333335,
        (1, 5): 3.2508333333333335, (1, 6): 3.2508333333333335, (1, 7): 3.2508333333333335}

    return led_tests(data)


def check_green_led():
    logger.info("Checking green LED")
    send_test_green_sysex_messages_to_midi_device()
    data = {(0, 0): 3.2508333333333335, (0, 1): 3.2508333333333335, (0, 2): 3.2508333333333335,
            (0, 3): 2.8434999999999997, (0, 4): 3.2430000000000003, (0, 5): 2.827833333333333,
            (0, 6): 2.7416666666666667, (0, 7): 2.8826666666666667, (1, 0): 2.804333333333333,
            (1, 1): 2.82, (1, 2): 2.827833333333333, (1, 3): 2.9061666666666666, (1, 4): 2.8121666666666663,
            (1, 5): 2.8826666666666667, (1, 6): 2.874833333333333, (1, 7): 2.8591666666666664}

    return led_tests(data)