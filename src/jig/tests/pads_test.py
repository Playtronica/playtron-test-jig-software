import time

from base_logger import get_logger_for_file
from jig.jig_hardware_control.ads1015_4052 import MultiplexerADCReader
from jig.tests.serial_tests import SerialTests

adc_read = MultiplexerADCReader()
logger = get_logger_for_file(__name__)


serial = SerialTests()

def pads_test():
    for multiplexer_num in range(4):
        for multiplexer_channel_num in range(4):
            adc_read.read_channel(multiplexer_num, multiplexer_channel_num)
            data = serial.last_data.copy()
            logger.info(data)

