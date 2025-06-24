import time

from base_logger import get_logger_for_file
from jig.jig_hardware_control.ads1015_4052 import MultiplexerADCReader

adc_read = MultiplexerADCReader()
logger = get_logger_for_file(__name__)

def test_pads_and_leds():
    for multiplexer_num in range(4):
        for multiplexer_channel_num in range(4):
            adc_val = adc_read.read_channel(multiplexer_num, multiplexer_channel_num)
            time.sleep(1)
            logger.info(f"Light sensor {multiplexer_num} {multiplexer_channel_num} -> {adc_val}")