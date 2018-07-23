[![Build Status](https://travis-ci.org/voidpp/PCA9685-driver.svg?branch=master)](https://travis-ci.org/voidpp/PCA9685-driver)
[![Coverage Status](https://coveralls.io/repos/github/voidpp/PCA9685-driver/badge.svg?branch=master)](https://coveralls.io/github/voidpp/PCA9685-driver?branch=master)

About
-----
Driver for PCA9685 controller. Datasheet: https://www.adafruit.com/datasheets/PCA9685.pdf

Install
-------
Some system packages are mandatory for `smbus-cffi`:
```bash
sudo apt-get install build-essential libi2c-dev i2c-tools python-dev libffi-dev
```

Now install the driver from pip
```bash
pip install PCA9685-driver
```

Example
-------
```py
from pca9685_driver import Device

# 0x40 from i2cdetect -y 1 (1 if Raspberry pi 2)
dev = Device(0x40)

# set the duty cycle for LED05 to 50%
dev.set_pwm(5, 2047)

# set the pwm frequency (Hz)
dev.set_pwm_frequency(1000)
```

Hardware environment
--------------------
This driver tested only with Raspberry Pi 2 and [Adafruit 16-Channel 12-bit PWM/Servo Driver](https://www.adafruit.com/products/815) 
