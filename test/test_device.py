import unittest

from pca9685_driver import Device, DeviceException

from pca9685_driver.tools.fake_smbus import FakeSMBus

class TestDevice(unittest.TestCase):

    def test_search_for_i2c_devices(self):
        # Arrange
        def glob(pattern):
            return ['/dev/i2c-8']

        # Act
        dev = Device(0, None, FakeSMBus, glob)

        # Assert
        self.assertEqual(dev.bus.bus_number, 8)

    def test_calc_pre_scale(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act & Assert
        self.assertEqual(dev.calc_pre_scale(200), 30)
        self.assertEqual(dev.calc_pre_scale(1000), 5)

    def test_set_pwm_frequency(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act
        dev.set_pwm_frequency(200)

        # Assert
        self.assertEqual(dev.bus.wrote_values[0], (0, 17))
        self.assertEqual(dev.bus.wrote_values[1], (254, 30))
        self.assertEqual(dev.bus.wrote_values[2], (0, 1))

    def test_set_pwm_frequency_wrong_input(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act & Assert
        with self.assertRaises(DeviceException):
            dev.set_pwm_frequency(2000)
        with self.assertRaises(DeviceException):
            dev.set_pwm_frequency(10)

    def test_led_number_getter(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act & Assert
        self.assertEqual(dev.led_0, 2047) # default value in FakeSMBus

    def test_led_number_wrong_getter(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act & Assert
        with self.assertRaises(AttributeError):
            self.assertEqual(dev.led_42, 2047)
        with self.assertRaises(AttributeError):
            self.assertEqual(dev.teve, 2047)

    def test_set_pwm_value(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act
        dev.set_pwm(4, 1042)

        # Assert
        self.assertEqual(dev.bus.values[24], 18)
        self.assertEqual(dev.bus.values[25], 4)

    def test_calc_frequency(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act & Assert
        self.assertEqual(dev.calc_frequency(30), 197)
        self.assertEqual(dev.calc_frequency(5), 1017)

    def test_get_pwm_frequency(self):
        # Arrange
        dev = Device(0, 0, FakeSMBus)

        # Act
        dev.set_pwm_frequency(197)

        # Assert
        self.assertEqual(dev.get_pwm_frequency(), 197)
