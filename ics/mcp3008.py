'''
Authors: Jeremy Blythe, Chris Fane

Original mcp3008 implementation completed by Jeremy Blythe.  Modularisation, extension for named pins and alternate bus addresses by Chris Fane

This module implements support for use the TextStar Serial LCD display in TTL mode form the Raspberry Pi.  Supporting 16*2 charactor output and the builtin bar graph functionality.  For usage information please consult the examples distributed with this package.
'''

import sys

import spidev

class MCP3008(object):
    
    def __init__(self, spi_address_hardware=0, spi_address_output=0):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        self.inputs = { 0 : { 'name' : "pin_0"},
                        1 : { 'name' : "pin_1"},
                        2 : { 'name' : "pin_2"},
                        3 : { 'name' : "pin_3"},
                        4 : { 'name' : "pin_4"},
                        5 : { 'name' : "pin_5"},
                        6 : { 'name' : "pin_6"},
                        7 : { 'name' : "pin_7"},}
        
    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def read_input(self, source_pin):
        try:
            # null op to throw exception if given non-ints.
            if int(source_pin) > 7 :
                raise Exception("Pin ID greater than 7 supplied, pin ids are zero referenced.")    
            #
            reading = self.spi.xfer2([1,(8+source_pin)<<4,0])
            return ((reading[1]&3) << 8) + reading[2]            
        except ValueError:
            # We're dealing with a named pin, do a lookup.
            for input_pin in self.inputs:
                if self.inputs[input_pin]['name'] == source_pin:
                    reading = self.spi.xfer2([1,(8+input_pin)<<4,0])
                    return ((reading[1]&3) << 8) + reading[2]
            else:
                raise Exception("No matches found for pin : %s " % source_pin)  
                
               
    def get_input(self, source_pin):
        # Alias of read_input
        return self.read_input(source_pin)

    def name_pin(self, pin_id=0, pin_name=None):
        
        if pin_name is None:
            raise Exception("Non pin name provided")
        try:
            # null op to throw exception if given non-ints.
            if int(pin_id) > 7 :
                raise Exception("Pin ID greater than 7 supplied, pin ids are zero referenced.")    
            
        except ValueError:
            raise Exception("Non integer Register or Pin ID supplied.")
        
        for input_pin in self.inputs:
            if self.inputs[input_pin]['name'] == pin_name:
                raise Exception("Pin Name %s is already in use on pin : %d " % (pin_name, input_pin))
        else:
            self.inputs[pin_id]['name'] = pin_name
                
