import os
import shutil
import re
import subprocess

import variables
from base_logger import get_logger_for_file


logger = get_logger_for_file(__name__)


firmware_file = None
def get_firmware_file():
    global firmware_file
    if firmware_file and firmware_file.is_file():
        logger.info(f"Use old firmware file {firmware_file}")
        return firmware_file

    firmware_file = None

    files = [f for f in os.listdir(variables.FIRMWARE_PATH)
             if os.path.isfile(os.path.join(variables.FIRMWARE_PATH, f)) and re.match(variables.FIRMWARE_PATTERN, f)
    ]
    if not files:
        logger.warn("Don't see any firmware files")
        return None

    files.sort()
    file = files[-1]
    if not file.endswith(".uf2"):
        logger.warn(f"File from firmware dir is not firmware. {file}")
        return None

    firmware_file = variables.FIRMWARE_PATH / file
    logger.info(f"Firmware file has been found. {file}")
    return firmware_file


def mount_usb_drive(drive_name):
    os.makedirs(variables.MOUNT_POINT, exist_ok=True)
    try:
        subprocess.run(['sudo', 'mount', f'/dev/{drive_name}', variables.MOUNT_POINT], check=True)
        logger.info(f"Mounted /dev/{drive_name} at {variables.MOUNT_POINT}")
    except subprocess.CalledProcessError as e:
        logger.warn(f"Failed to mount /dev/{drive_name}: {e}")


def is_device_connected():
    lsblk_output = subprocess.check_output(['lsblk', '-o', 'NAME,TYPE,MOUNTPOINT'], text=True)

    for line in lsblk_output.splitlines()[1:]:
        parts = line.split()
        logger.info(parts)
        if len(parts) == 3 and parts[1] == 'part' and parts[2] == str(variables.MOUNT_POINT):
            return True

        if len(parts) == 2 and parts[1] == 'part':
            mount_usb_drive(parts[0][2:])
            return True

    return False


def unmount_usb_drive():
    try:
        subprocess.run(['sudo', 'umount', variables.MOUNT_POINT], check=True)
        logger.info(f"Umounted {variables.MOUNT_POINT}")
    except subprocess.CalledProcessError as e:
        logger.warn(f"Failed to unmount {variables.MOUNT_POINT}: {e}")


def copy_firmware_to_usb_drive(source_file):
    destination = os.path.join(variables.MOUNT_POINT, os.path.basename(source_file))
    try:
        shutil.copy2(source_file, destination)  # Copy the file
        logger.info(f"File '{source_file}' has been copied to device.")
        return True
    except Exception as e:
        logger.warn(f"Failed to copy to device: {e}")
        return False


def load_firmware_to_device():
    source_file = get_firmware_file()
    if not source_file:
        logger.warn("Some problem with loading firmware file")
        return "FIRMWARE_NOT_FOUND"
    logger.info(f"Firmware has been found")

    if not is_device_connected():
        logger.warn("Cant find any devices")
        return "DEVICE_NOT_FOUND"
    logger.info(f"Device has been found")

    if not copy_firmware_to_usb_drive(source_file):
        logger.warn("Failed to copy firmware file")
        return "CP_FIRMWARE_ERROR"

    logger.info(f"Firmware has been copied to usb drive")
    unmount_usb_drive()



if __name__ == "__main__":
    load_firmware_to_device()