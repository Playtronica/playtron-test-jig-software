import logging

import smbus2 as smbus

# Default TCA9535 address (can vary depending on A0-A2 pin settings)
TCA9535_ADDRESS = 0x20

# Configuration register (0x06 for port 0, 0x07 for port 1)
CONFIG_PORT_0 = 0x06
CONFIG_PORT_1 = 0x07

# Output register (0x02 for port 0, 0x03 for port 1)
OUTPUT_PORT_0 = 0x02
OUTPUT_PORT_1 = 0x03

class TCA9535:
    def __init__(self, i2c_address=TCA9535_ADDRESS, bus_number=1):
        self.address = i2c_address
        self.bus = smbus.SMBus(bus_number)

        # Set the output state of all pins to 0 (low) before setting configuration
        self.write_register(OUTPUT_PORT_0, 0x00)  # Set all pins of port 0 to low
        self.write_register(OUTPUT_PORT_1, 0x00)  # Set all pins of port 1 to low

        # Now set the direction for all pins to output (0x00 means all pins are outputs)
        self.config_port_0 = 0x00  # All pins of port 0 as output
        self.config_port_1 = 0x00  # All pins of port 1 as output

        # Write the configuration to the TCA9535
        self.write_register(CONFIG_PORT_0, self.config_port_0)
        self.write_register(CONFIG_PORT_1, self.config_port_1)

        # Now that the configuration is set, read the initial state of output ports
        self.output_port_0 = self.read_register(OUTPUT_PORT_0)  # Read current state of port 0
        self.output_port_1 = self.read_register(OUTPUT_PORT_1)  # Read current state of port 1

        # Print the current state of the output ports
        logging.debug(f"Output Port 0: 0b{self.output_port_0:08b}")  # Using self.output_port_0
        logging.debug(f"Output Port 1: 0b{self.output_port_1:08b}")  # Using self.output_port_1

    def write_register(self, register, value):
        """Write a value to the specified register"""
        self.bus.write_byte_data(self.address, register, value)

    def read_register(self, register):
        """Read the value from the specified register"""
        return self.bus.read_byte_data(self.address, register)

    def set_pin(self, port, pin, state):
        """
        Set the state of an individual pin on a port.
        
        port: Port number (0 or 1)
        pin: Pin number (0-7)
        state: State (1 - high, 0 - low)
        """
        if port == 0:
            output_register = OUTPUT_PORT_0
            current_state = self.read_register(OUTPUT_PORT_0)  # Read current state of port 0
        elif port == 1:
            output_register = OUTPUT_PORT_1
            current_state = self.read_register(OUTPUT_PORT_1)  # Read current state of port 1
        else:
            raise ValueError("Invalid port number. Use 0 or 1.")

        # Log current state after reading
        #print(f"Current state of port {port} before modification: 0b{current_state:08b}")

        if state:
            current_state |= (1 << pin)  # Set bit
        else:
            current_state &= ~(1 << pin)  # Clear bit

        # Write new state to the output register
        self.write_register(output_register, current_state)

        # Log current state after writing
        #print(f"Current state of port {port} after modification: 0b{current_state:08b}")

        # Read and log the state of the port again after writing to confirm
        #new_state = self.read_register(output_register)
        #print(f"Confirmed state of port {port} after writing: 0b{new_state:08b}")

        # Update the local variable for port state
        if port == 0:
            self.output_port_0 = current_state
        else:
            self.output_port_1 = current_state
