import spidev
import time
import math 

import sys

HIGH = 'high'
LOW = 'low'

class Shift_Register(object):
    
    def __init__(self, registers_in_chain=1, spi_address_hardware=0, spi_address_output=0):
        self.number_of_registers = registers_in_chain
        self.inverse_range = []
        for i in range(self.number_of_registers): 
            self.inverse_range.insert(0, i)
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        self.pins = {}
        
        self.pin_count = self.number_of_registers* 8
        
        for pin in range(self.pin_count):
            self.pins[pin] = { 'state' : 0 , 'name' : "pin_%d" % pin }
        
        self.write()
        
           
    def write(self):
        # used to flush current register state to IC.
        byte_list = []
        byte_string = ""
        for pin in self.pins:
            byte_string = "%s%s" % (self.pins[pin]['state'],byte_string)
            if len(byte_string) == 8:
                byte_list.append(int(byte_string, 2))
                byte_string = ""

        # flip our list to fill the IC chain deepest first.
        byte_list.reverse()
        self.spi.xfer2(byte_list)
        
        
    def set(self):
        # Alias of write
        return self.write()

    def print_pins(self):
        print self.pins
        
    def set_pin(self, pin_id, state=None,):
        # Check we've been given a valid state.
            
        if state.lower() not in ['high','low']:
            raise Exception("Invalid state : %s , for pin : %s, valid states are high & low" % (state, pin_id))
        else:
            if state.lower() == 'high':
                state = 1
            else:
                state = 0
       
        try:
            # null op to check if the we've been given a pin name.
            int(pin_id)
            self.pins[pin_id]['state'] = state 
        except ValueError:
            for pin in self.pins:
                if self.pins[pin]['name'] == pin_id:
                    self.pins[pin]['state'] = state 
                    break
            else:
                raise Exception("No matches found for pin : %s " % pin_id)    
                    
       
    def name_pin(self, pin_id, pin_name=None):
        
        if pin_name is None:
            raise Exception("Non pin name provided")
        try:
            # null op to throw exception if given non-ints.
            int(pin_id)
        except ValueError:
            raise Exception("Non integer Register or Pin ID supplied.")
        
        for pin in self.pins:
            if self.pins[pin]['name'] == pin_name:
                raise Exception("Pin Name %s is already in use on pin : %d " % (pin_name, pin))
        else:
            self.pins[pin_id]['name'] = pin_name
                
                
    def binary_count(self):
        # run a binary count, without destroying current pin state.  Useful for testing connections.
        bytes_dict = {}
        for i in range(self.number_of_registers):
            bytes_dict[i] = 0
        
        registers_full = False
                
        while not registers_full:
            bytes_dict[0] = bytes_dict[0] +1
            bytes_list = []
            for i in range(self.number_of_registers):
                if bytes_dict[i] == 256:
                    bytes_dict[i] = 0
                    if i < self.number_of_registers:
                        try:
                            bytes_dict[i +1] = bytes_dict[i +1] +1
                        except KeyError:
                            registers_full = True
                            break
                
                bytes_list.insert(0, bytes_dict[i])

            if not registers_full:
                self.spi.xfer2(bytes_list)
                time.sleep(0.05)   
        
            
    def all_on(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for register in range(self.number_of_registers):
            byte_list.append(255)
        self.spi.xfer2(byte_list)
        
    def all_off(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for register in range(self.number_of_registers):
            byte_list.append(0)
        self.spi.xfer2(byte_list)
        
    def set_on(self):
        for pin in self.pins:
            self.pins[pin]['state'] = 1
        
    def set_off(self):
        for pin in self.pins:
            self.pins[pin]['state'] = 0
                