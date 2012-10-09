#!/usr/bin/env python
# - * - Coding: utf-8 - * -
'''
For information on circuit construction, please consult the fritzing diagram included with this package.
'''


from time import sleep

from pigredients.ics import mcp3008 as mcp3008
from pigredients.displays import textStarSerialLCD as textStarSerialLCD

# Using standard addresses so no need for any params.
adc_instance = mcp3008.MCP3008()

display = None

def write_pots():
    display.position_cursor(1, 1)
    val = adc_instance.read_input(2)
    percent = int(val/10.23)
    display.ser.write(str(val).ljust(16))
    display.capped_bar(16, percent)
    print "Current Pin 0 Val : %d " % val

# Callbacks
def on_page():
    display.clear()
    display.window_home()
    if display.page == 'a':
        write_pots()
        
def on_tick():
    if display.page == 'a':
        write_pots()

def on_refresh():
    if display.page == 'a':
        write_pots()

display = textStarSerialLCD.Display(on_page, on_tick, on_refresh)            
display.run()
    
