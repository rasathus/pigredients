#!/usr/bin/env python
from setuptools import setup, find_packages
from pigredients import __version__

setup(name="pigredients",
      version=__version__,
      description="An Integrated Circuit, Display and Sensor library, providing integration between a number of hardware components and the Raspberry Pi.",
      license="MIT",
      author="Chris Fane",
      author_email="pigredients@chrisfane.co.uk",
      url="https://github.com/rasathus/pigredients",
      packages = find_packages(),
      keywords= "RaspberryPi Raspberry Pi 74hc595 mcp3008 ws2801 hmc5883l",
      python_requires=">=3.9",
      install_requires=["spidev"],
      # Per-module optional dependencies.  The I2C modules (mpu6050, hmc5883l)
      # additionally need the 'smbus' module and Adafruit_I2C, which are not
      # installable from PyPI as-is, so no 'i2c' extra is declared.
      extras_require={"serial": ["pyserial"]},
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
      ],
      zip_safe = True)
