[![Build Status](https://travis-ci.org/voidpp/PCA9685-driver.svg?branch=master)](https://travis-ci.org/voidpp/PCA9685-driver)

Driver for PCA9685 controller. Datasheet: https://www.adafruit.com/datasheets/PCA9685.pdf

Example
-
```py
from pca9685_driver import Device

# 0x40 from i2cdetect -y 1 (1 if Raspberry pi 2)
dev = Device(0x40) 

# set the duty cycle for LED05 to 50%
dev.set_pwm(5, 2047)

# set the pwm frequency (Hz)
dev.set_pwm_frequency(1000)
```
