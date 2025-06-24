import time

from base_logger import get_logger_for_file
from jig.jig_hardware_control.ads1015_4052 import MultiplexerADCReader
from jig.tests.serial_tests import SerialTests

adc_read = MultiplexerADCReader()
logger = get_logger_for_file(__name__)


serial = SerialTests()

def pads_test():
    pads_id = set()
    for multiplexer_num in range(4):
        for multiplexer_channel_num in range(4):
            adc_read.read_channel(multiplexer_num, multiplexer_channel_num)
            data = serial.last_data.copy()
            logger.info(data)

            if ("status" not in data) or (data["status"] != "pressed"):
                logger.warn("Strange json")
                return "STRANGE JSON"

            if ("pad_id" not in data) or (type(data["pad_id"]) is not int):
                logger.warn("Strange json")
                return "STRANGE JSON"

            pads_id.add(data["pad_id"])

    if set(range(16)) != pads_id:
        logger.warn("Not all pads or redundant")
        return "PADS NOT CORRECT"

    return

