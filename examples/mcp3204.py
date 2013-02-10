#!/usr/bin/env python
# - * - Coding: utf-8 - * -

from time import sleep

from pigredients.ics import mcp3204 as mcp3204

adc_instance = mcp3204.MCP3204(spi_address_output=1)

def get_vals():
    for input_pin in [0,1]:
        val = adc_instance.read_input(input_pin)
        print "Current Pin %d Val : %d " % (input_pin, val)

while True:
    get_vals()
    sleep(1)
