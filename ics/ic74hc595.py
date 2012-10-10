import spidev
import time

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
        self.registers = {}
        for register in range(self.number_of_registers):
            self.registers[register] = {    0 : { 'state' : 0 , 'name' : "register_%d_pin_0" % register },
                                            1 : { 'state' : 0 , 'name' : "register_%d_pin_1" % register },
                                            2 : { 'state' : 0 , 'name' : "register_%d_pin_2" % register },
                                            3 : { 'state' : 0 , 'name' : "register_%d_pin_3" % register },
                                            4 : { 'state' : 0 , 'name' : "register_%d_pin_4" % register },
                                            5 : { 'state' : 0 , 'name' : "register_%d_pin_5" % register },
                                            6 : { 'state' : 0 , 'name' : "register_%d_pin_6" % register },
                                            7 : { 'state' : 0 , 'name' : "register_%d_pin_7" % register },}
        
        self.write()
        
           
    def write(self):
        # used to flush current register state to IC.
        byte_list = []
        for register in self.registers:
            byte_string = ""
            for pin in self.registers[register]:
                byte_string = "%s%s" % (self.registers[register][pin]['state'],byte_string)
            byte_list.append(int(byte_string, 2))
        # flip our list to fill the IC chain deepest first.
        byte_list.reverse()
        print "post byte_list : %s" % byte_list
        self.spi.xfer2(byte_list)
        
        
    def set(self):
        # Alias of write
        return self.write()

    def print_registers(self):
        print self.registers
        
    def set_pin(self, pin_id=0, state=None, pin_name=None, register_id=0):
        # Check we've been given a valid state.
            
        if state not in ['high','low']:
            raise Exception("Invalid state : %s , for pin : %s, valid states are high & low" % (state, pin_id))
        else:
            if state == 'high':
                state = 1
            else:
                state = 0
                
        # Check if we've been given an id or a name
        if pin_name is not None:
            # Looks like we've been given a name.
            # checking our registers for an instance of the name.
            for register in self.registers:
                for pin in self.registers[register]:
                    if self.registers[register][pin]['name'] == pin_name:
                        self.registers[register_id][pin_id]['state'] = state 
                        break
                else:
                    raise Exception("No matches found for pin : %s " % pin_name)    
        else:
            # We must be using pin ids then.
            try:
                # null op to throw exception if given non-ints.
                if int(pin_id) > 7 :
                    raise Exception("Pin ID greater than 7 supplied, pin ids are zero referenced.")    
                int(register_id)
            except ValueError:
                raise Exception("Non integer Register or Pin ID supplied.")
            
            try:
                self.registers[register_id][pin_id]['state'] = state 
            except KeyError:
                raise Exception("Invalid Register id, please ensure you've initialised it before writing to it.")

    def name_pin(self, pin_id=0, pin_name=None, register_id=0):
        
        if pin_name is None:
            raise Exception("Non pin name provided")
        try:
            # null op to throw exception if given non-ints.
            if int(pin_id) > 7 :
                raise Exception("Pin ID greater than 7 supplied, pin ids are zero referenced.")    
            int(register_id)
        except ValueError:
            raise Exception("Non integer Register or Pin ID supplied.")
        
        for register in self.registers:
            for pin in self.registers[register]:
                if self.registers[register][pin]['name'] == pin_name:
                    raise Exception("Pin Name %s is already in use on register : %d pin : %d " % (pin_name, register, pin))
            else:
                self.registers[register_id][pin_id]['name'] = pin_name
                
    def binary_count(self):
        # run a binary count, without destroying current pin state.  Useful for testing connections.
        bytes_dict = {}
        for i in range(self.number_of_registers):
            bytes_dict[i] = 0
        
        print "bytes_dict, how many registers ? : %s" % bytes_dict
        print "range : %s" % range(self.number_of_registers)
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
                for register in self.inverse_range :
                    self.spi.xfer2([bytes_list[register]])  
                time.sleep(0.05)   
        
            
    def all_on(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for register in self.registers:
            byte_list.append(255)
        self.spi.xfer2(byte_list)
        
    def all_off(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for register in self.registers:
            byte_list.append(0)
        self.spi.xfer2(byte_list)
        
    def set_on(self):
        for register in self.registers:
            for pin in self.registers[register]:
                self.registers[register][pin]['state'] = 1
        
    def set_off(self):
        for register in self.registers:
            for pin in self.registers[register]:
                self.registers[register][pin]['state'] = 0        
                