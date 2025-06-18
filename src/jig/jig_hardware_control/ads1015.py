import smbus2 as smbus
import time

# Addresses of the devices on the I2C bus
ADS1015_ADDRESS_1 = 0x48  # Address of the first ADC
ADS1015_ADDRESS_2 = 0x4B  # Address of the second ADC

# Pointer register
ADS1015_REG_POINTER_CONVERT = 0x00
ADS1015_REG_POINTER_CONFIG = 0x01

# Basic configuration settings
ADS1015_CONFIG_OS_SINGLE = 0x8000  # Start a single conversion
ADS1015_CONFIG_MODE_SINGLE = 0x0100  # Single-shot mode

# Multiplexer settings (for single-ended measurements)
ADS1015_MUX_SINGLE_0 = 0x4000  # Channel 0
ADS1015_MUX_SINGLE_1 = 0x5000  # Channel 1
ADS1015_MUX_SINGLE_2 = 0x6000  # Channel 2
ADS1015_MUX_SINGLE_3 = 0x7000  # Channel 3

# PGA settings (gain)
ADS1015_PGA_6_144V = 0x0000  # +/-6.144V range
ADS1015_PGA_4_096V = 0x0200  # +/-4.096V range
ADS1015_PGA_2_048V = 0x0400  # +/-2.048V range (default)
ADS1015_PGA_1_024V = 0x0600  # +/-1.024V range
ADS1015_PGA_0_512V = 0x0800  # +/-0.512V range
ADS1015_PGA_0_256V = 0x0A00  # +/-0.256V range

ADS1015_CONFIG_CQUE_NONE = 0x0003 # Disable the comparator and put ALERT/RDY in high state (default)

# Data rate settings
ADS1015_DR_1600SPS = 0x0080  # 1600 samples per second (default)

class ADS1015:
    def __init__(self, i2c_bus=1):
        self.bus = smbus.SMBus(i2c_bus)
        self.address_1 = ADS1015_ADDRESS_1
        self.address_2 = ADS1015_ADDRESS_2

    def _write_register(self, address, reg, value):
        """Writes a 16-bit value to the specified register on the given address."""
        self.bus.write_i2c_block_data(address, reg, [(value >> 8) & 0xFF, value & 0xFF])

    def _read_register(self, address, reg):
        """Reads a 16-bit value from the specified register on the given address."""
        data = self.bus.read_i2c_block_data(address, reg, 2)
        return (data[0] << 8) | data[1]

    def read_single_channel(self, channel, pga=ADS1015_PGA_2_048V, sps=ADS1015_DR_1600SPS):
        """Reads the value from one of the ADC channels (0-7) and returns it in volts, accounting for a voltage divider."""
        # Define voltage ranges for each PGA setting
        voltage_range = {
            ADS1015_PGA_6_144V: 6.144,
            ADS1015_PGA_4_096V: 4.096,
            ADS1015_PGA_2_048V: 2.048,
            ADS1015_PGA_1_024V: 1.024,
            ADS1015_PGA_0_512V: 0.512,
            ADS1015_PGA_0_256V: 0.256
        }

        # Set addresses based on channel selection
        if 0 <= channel <= 3:
            address = self.address_1
            mux = [ADS1015_MUX_SINGLE_0, ADS1015_MUX_SINGLE_1, ADS1015_MUX_SINGLE_2, ADS1015_MUX_SINGLE_3][channel]
        elif 4 <= channel <= 7:
            address = self.address_2
            mux = [ADS1015_MUX_SINGLE_0, ADS1015_MUX_SINGLE_1, ADS1015_MUX_SINGLE_2, ADS1015_MUX_SINGLE_3][channel - 4]
        else:
            raise ValueError("Invalid channel number: choose from 0 to 7.")

        config = ADS1015_CONFIG_OS_SINGLE | mux | pga | sps | ADS1015_CONFIG_MODE_SINGLE

        # Write configuration and start conversion
        self._write_register(address, ADS1015_REG_POINTER_CONFIG, config)

        # Wait for conversion to complete
        time.sleep(0.001)

        # Read the raw result
        result = self._read_register(address, ADS1015_REG_POINTER_CONVERT)
        raw_value = result >> 4  # ADS1015 returns 12-bit values, so shift right by 4 bits

        # Log the raw ADC result in hex format
        # print(f"Raw ADC value (hex): {hex(raw_value)}")

        # Convert the raw value to voltage
        max_voltage = voltage_range.get(pga, 2.048)  # Default to 2.048V if PGA is unknown
        voltage = (raw_value / 2048.0) * max_voltage  # 2048 is the midpoint for 12-bit ADC

        # Compensation for the voltage divider (820kΩ and 120kΩ)
        divider_coefficient = 1 + (820 / 120)  # Calculation based on the resistor values
        real_voltage = voltage * divider_coefficient

        # Log the real voltage before returning
        # print(f"Real voltage: {real_voltage:.3f} V (compensated for voltage divider)")

        return real_voltage


    def read_and_check_range(self, channel, min_value, max_value, pga=ADS1015_PGA_2_048V, sps=ADS1015_DR_1600SPS):
        """
        Reads the value from channel (0-7) and checks if it falls within the specified range.
        Returns 1 if the value is within the range, and 0 if it's outside.
        """
        try:
            # Read the value from the selected channel
            value = self.read_single_channel(channel, pga, sps)
            # print(f"Read value from channel {channel}: {value}")
            
            # Check if the value falls within the range
            if min_value <= value <= max_value:
                # print(f"Value {value} is within the range {min_value}-{max_value}")
                return 1
            else:
                # print(f"Value {value} is outside the range {min_value}-{max_value}")
                return 0
        except Exception as e:
            # print(f"Error: {e}")
            return 0

    def read_and_check_multiple_channels(self, channels, min_value, max_value, pga=ADS1015_PGA_2_048V, sps=ADS1015_DR_1600SPS):
        """
        Reads the values from multiple ADC channels and checks if they fall within the specified range.
        
        :param channels: A list of channels (0-7) to check.
        :param min_value: The minimum acceptable value.
        :param max_value: The maximum acceptable value.
        :param pga: Programmable gain amplifier setting.
        :param sps: Samples per second setting.
        
        :return: 1 if all channels are within the range, 0 if any channel is outside the range.
        """
        all_in_range = True  # Инициализируем общий результат как True (все в пределах диапазона)

        for channel in channels:
            try:
                # Read the value from the selected channel
                value = self.read_single_channel(channel, pga, sps)
                # print(f"Read value from channel {channel}: {value}")
                
                # Check if the value falls within the range
                if min_value <= value <= max_value:
                    # print(f"Value {value} on channel {channel} is within the range {min_value}-{max_value}")
                    pass
                else:
                    # print(f"Value {value} on channel {channel} is outside the range {min_value}-{max_value}")
                    all_in_range = False  # Если хотя бы один канал не соответствует условиям, общий результат становится False
            except Exception as e:
                # print(f"Error reading channel {channel}: {e}")
                all_in_range = False  # В случае ошибки чтения считаем, что канал не соответствует условиям

        return 1 if all_in_range else 0  # Возвращаем 1 если все в пределах диапазона, иначе 0
