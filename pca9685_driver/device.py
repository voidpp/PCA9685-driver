import smbus
import logging
import glob
import re

logger = logging.getLogger(__name__)

class DeviceException(Exception):
    pass

class Registers(object):
    MODE_1 = 0x00
    MODE_2 = 0x01
    LED_STRIP_START = 0x06 # LED0 ON Low Byte
    PRE_SCALE = 0xFE

class Mode1(object):
    RESTART = 7
    EXTCLK = 6
    AI = 5
    SLEEP = 4
    SUB1 = 3
    SUB2 = 2
    SUB3 = 1
    ALLCALL = 0

class Mode2(object):
    INVRT = 4
    OCH = 3
    OUTDRV = 2
    OUTNE_1 =1
    OUTNE_0 = 0

def value_low(val):
    return val & 0xFF

def value_high(val):
    return (val >> 8) & 0xFF

class Device(object):

    ranges = dict(
        pwm_frequency = (24, 1526),
        led_number = (0, 15),
        led_value = (0, 4095),
        register_value = (0, 255),
    )

    def __init__(self, address, bus_number = None, bus_interface_factory = smbus.SMBus, glober = glob.glob):
        """Creates an interface to PCA9685 device

        :param address: the I2C address of the device. Check the addressed with `i2cdetect -y 1`
        :param bus_number: the number of the I2C bus in the linux machine. See /dev/i2c-*
        :param bus_interface_factory: bus class factory, used for unit tests
        :param glober: for search in file system, used for unit tests
        """

        if bus_number is None:
            bus_list = Device.get_i2c_bus_numbers(glober)
            if len(bus_list) < 1:
                raise DeviceException("Cannot determine I2C bus number")
            bus_number = bus_list[0]

        self.__address = address
        self.__bus = bus_interface_factory(bus_number)
        self.__oscillator_clock = 25000000

    @staticmethod
    def get_i2c_bus_numbers(glober = glob.glob):
        """Search all the available I2C devices in the system"""
        res = []
        for device in glober("/dev/i2c-*"):
            r = re.match("/dev/i2c-([\d]){1,2}", device)
            res.append(int(r.group(1)))
        return res

    @property
    def mode_1(self):
        """Returns the Mode 1 register value"""
        return self.read(Registers.MODE_1)

    @property
    def bus(self):
        """Returns the bus instance"""
        return self.__bus

    def get_led_register_from_name(self, name):
        """Parse the name for led number

        :param name: attribute name, like: led_1
        """
        res = re.match('^led_([0-9]{1,2})$', name)
        if res is None:
            raise AttributeError("Unknown attribute: '%s'" % name)
        led_num = int(res.group(1))
        if led_num < 0 or led_num > 15:
            raise AttributeError("Unknown attribute: '%s'" % name)
        return self.calc_led_register(led_num)

    def calc_led_register(self, led_num):
        """Calculate register number for LED pin

        :param led_num: the led number, typically 0-15
        """
        start = Registers.LED_STRIP_START + 2
        return start + (led_num * 4)

    def __check_range(self, type, value):
        range = self.ranges[type]
        if value < range[0]:
            raise DeviceException("%s must be greater than %s, got %s" % (type, range[0], value))
        if value > range[1]:
            raise DeviceException("%s must be less than %s, got %s" % (type, range[1], value))

    def set_pwm(self, led_num, value):
        """Set PWM value for the specified LED

        :param led_num: LED number (0-15)
        :param value: the 12 bit value (0-4095)
        """
        self.__check_range('led_number', led_num)
        self.__check_range('led_value', value)

        register_low = self.calc_led_register(led_num)

        self.write(register_low, value_low(value))
        self.write(register_low + 1, value_high(value))

    def __get_led_value(self, register_low):
        low = self.read(register_low)
        high = self.read(register_low + 1)
        return low + (high * 256)

    def get_pwm(self, led_num):
        """Generic getter for all LED PWM value"""
        self.__check_range('led_number', led_num)
        register_low = self.calc_led_register(led_num)
        return self.__get_led_value(register_low)

    def __getattr__(self, name):
        """Generic getter property handler for all LED PWM value"""
        register_low = self.get_led_register_from_name(name)
        return self.__get_led_value(register_low)

    def sleep(self):
        """Send the controller to sleep"""
        logger.debug("Sleep the controller")
        self.write(Registers.MODE_1, self.mode_1 | (1 << Mode1.SLEEP))

    def wake(self):
        """Wake up the controller"""
        logger.debug("Wake up the controller")
        self.write(Registers.MODE_1, self.mode_1 & (255 - (1 << Mode1.SLEEP)))

    def write(self, reg, value):
        """Write raw byte value to the specified register

        :param reg: the register number (0-69, 250-255)
        :param value: byte value
        """
        # TODO: check reg: 0-69, 250-255
        self.__check_range('register_value', value)
        logger.debug("Write '%s' to register '%s'" %  (value, reg))
        self.__bus.write_byte_data(self.__address, reg, value)

    def read(self, reg):
        """Read data from register

        :param reg: the register number (0-69, 250-255)
        """
        return self.__bus.read_byte_data(self.__address, reg)

    def calc_pre_scale(self, frequency):
        """Calculate the controller's PRE_SCALE value, specified by the PCA9685 datasheet

        :param frequency: source frequency value
        """
        return int(round(self.__oscillator_clock / (4096.0 * frequency)) - 1)

    def set_pwm_frequency(self, value):
        """Set the frequency for all PWM output

        :param value: the frequency in Hz
        """
        self.__check_range('pwm_frequency', value)
        reg_val = self.calc_pre_scale(value)
        logger.debug("Calculated prescale value is %s" % reg_val)
        self.sleep()
        self.write(Registers.PRE_SCALE, reg_val)
        self.wake()

    def calc_frequency(self, prescale):
        """Calculate the frequency by the controller's prescale, specified by the PCA9685 datasheet

        :param prescale: the prescale value of the controller
        """
        return int(round(self.__oscillator_clock / ((prescale + 1) * 4096.0)))

    def get_pwm_frequency(self):
        """Gets the frequency for all PWM output"""

        return self.calc_frequency(self.read(Registers.PRE_SCALE))
