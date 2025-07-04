import time

import mido
import mido.backends.rtmidi

from base_logger import get_logger_for_file
logger = get_logger_for_file(__name__)

midi_output = None

sysex_test_mode = mido.Message.from_bytes([240, 11, 20, 13, 0, 247])
sysex_enable_logs = mido.Message.from_bytes([240, 11, 20, 13, 2, 247])

def find_midi_device():
    try:
        global midi_output
        if midi_output:
            logger.info("Device has already been initialized")
            return "Device has already been Found"

        print(mido.get_output_names())
        for output_device in mido.get_output_names():
            if "Playtron" in output_device:
                logger.info("Playtron was found")
                midi_output = mido.open_output(output_device)
                return
        return "Device Not Found"
    except Exception as e:
        logger.error(f"Some error while connecting to playtron: {e}")
        return "Failed to connect to device"


def close_midi_connection_from_device():
    try:
        global midi_output
        if not midi_output:
            logger.info("Device is not enabled")
            return "Device Not Found"

        midi_output.close()
        midi_output = None
    except Exception as e:
        logger.error(f"Some error while closing midi device: {e}")
        return "Failed to close midi device"


def send_sysex_messages_to_midi_device(sysex_message):
    try:
        if not midi_output:
            logger.warn("MIDI Device is not found")
            return "Device Not Found"

        midi_output.send(sysex_message)
        time.sleep(0.1)
    except Exception as e:
        logger.error(f"Some error while sending debug sys ex: {e}")
        return "Failed to send debug sys ex"


def send_test_sysex_messages_to_midi_device():
    return send_sysex_messages_to_midi_device(sysex_test_mode)


def send_enable_logs_sysex_messages_to_midi_device():
    return send_sysex_messages_to_midi_device(sysex_enable_logs)

