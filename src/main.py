import re

import variables

from base_logger import get_logger_for_file
import subprocess

from firmware_updater import update_firmware_files
from jig.JigEnvironment import JigEnvironment
from jig.tests.load_firmware_to_device import load_firmware_to_device

logger = get_logger_for_file(__name__)


def check_internet_connection():
    try:
        subprocess.check_output(["ping", "-c", "1", "www.baidu.com"])
        logger.info("Internet connection established")
        return True
    except subprocess.CalledProcessError:
        logger.error("Internet connection error")
        return False


def initial_part():
    res = check_internet_connection()
    if res:
        update_firmware_files('Playtronica', 'playtron-releases')
    else:
        logger.error("Internet connection error")

    # TODO Was written without device in hands, rewrite when is possible
    import os
    files = [f for f in os.listdir(variables.FIRMWARE_PATH) if os.path.isfile(os.path.join(variables.FIRMWARE_PATH, f))
             and re.match(variables.FIRMWARE_PATTERN, f)]
    if not files:
        logger.warn("Don't see any firmware files")
        return None

    files.sort()
    file = files[-1]
    if not file.endswith(".uf2"):
        logger.warn(f"File from firmware dir is not firmware. {file}")
        return None

    version_str = file.split('_v')[-1].split('.uf2')[0]

    major, minor, patch = version_str.split('.')

    custom_major = major[-1]
    custom_minor = minor.zfill(2) if len(minor) < 2 else minor[-2:]
    custom_patch = patch.zfill(2) if len(patch) < 2 else patch[-2:]

    custom_version = f"{custom_major}.{custom_minor}.{custom_patch}"
    variables.DEVICE_FIRMWARE_VERSION = custom_version


if __name__ == '__main__':
    initial_part()
    print(variables.DEVICE_FIRMWARE_VERSION)

    jig = JigEnvironment()
    jig.init_jig_main_cycle()



