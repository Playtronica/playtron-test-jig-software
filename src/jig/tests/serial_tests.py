import serial
from threading import Thread
from base_logger import get_logger_for_file


logger = get_logger_for_file(__name__)

class SerialTests:
    _instance = None

    def __init__(self):
        self.is_enabled = False
        self.serial = None
        self.thread = None

        self.last_data = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def start_serial(self):
        if self.is_enabled:
            logger.warn("Serial thread has already been enabled")
            return "SERIAL ALREADY ENABLED"
        self.is_enabled = True
        self.serial = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
        self.thread = Thread(target=self.__process)
        self.thread.start()


    def stop_serial(self):
        if not self.is_enabled:
            logger.warn("Serial thread has not already been enabled")
            return "SERIAL DISABLED"
        self.is_enabled = False
        self.thread.join()
        self.serial.close()
        self.serial = None
        self.thread = None

    def __process(self):
        try:
            while self.is_enabled:
                line = self.serial.readline().decode("ascii")
                if not line or line[0] != "{":
                    logger.warn(f"Some problems with logs {line}")
                    continue
                self.last_data = eval(line)

        except Exception as e:
            logger.error("Exception while reading serial data: {}".format(e))
            self.is_enabled = False
            self.serial.close()
            self.serial = None
            self.thread = None