from setuptools import setup, find_packages

setup(
    name = "PCA9685-driver",
    description = "Driver module for PCA9685 pwm (LED/Servo) controller",
    version = "1.2.0",
    author = 'Lajos Santa',
    author_email = 'santa.lajos@coldline.hu',
    url = 'https://github.com/voidpp/PCA9685-driver.git',
    install_requires = [
        "smbus-cffi==0.5.1",
    ],
    include_package_data = True,
    packages = find_packages(),
)
