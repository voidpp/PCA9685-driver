
from pca9685_driver.device import Registers

class FakeSMBus(object):
    def __init__(self, bus_number):
        self.values = {
            Registers.MODE_1: 0b00010001,
            8: 255,
            9: 7,
        }
        self.wrote_values = []
        self.bus_number = bus_number

    def write_byte_data(self, address, register, value):
        self.values[register] = value
        self.wrote_values.append((register, value))

    def read_byte_data(self, address, register):
        return self.values[register]
