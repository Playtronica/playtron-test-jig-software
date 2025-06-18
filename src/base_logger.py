import logging
import time
from variables import LOGGER_PATH

base_logger = logging.getLogger("biotron_test_jig")

base_logger.setLevel(logging.INFO)

name_of_file = time.strftime("%Y.%m.%d.%H.%M.%S")
file_handler = logging.FileHandler(LOGGER_PATH / f'{name_of_file}.log', mode="w+")
# stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")


file_handler.setFormatter(formatter)
# stream_handler.setFormatter(formatter)
base_logger.addHandler(file_handler)
# base_logger.addHandler(stream_handler)

def get_logger_for_file(name):
    return base_logger.getChild(name)