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
      zip_safe = True)
