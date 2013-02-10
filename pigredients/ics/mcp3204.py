import sys

import spidev

class MCP3204(object):
    
    def __init__(self, spi_address_hardware=0, spi_address_output=0):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        self.inputs = { 0 : { 'name' : "pin_0"},
                        1 : { 'name' : "pin_1"},
                        2 : { 'name' : "pin_2"},
                        3 : { 'name' : "pin_3"}}
        
    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def read_input(self, source_pin):
        try:
            # null op to throw exception if given non-ints.
            if int(source_pin) > 3 :
                raise Exception("Pin ID greater than 3 supplied, pin ids are zero referenced.") 
            read_payload = [6,source_pin<<6,0]
            #print "Reading payload for %d : %s" % (source_pin, read_payload)
            reading = self.spi.xfer2(read_payload)
            result = (reading[1] << 8 | reading[2]) 
            #print "Reading from %d : %s" % (source_pin, result)
            return result
        except ValueError:
            # We're dealing with a named pin, do a lookup.
            for input_pin in self.inputs:
                if self.inputs[input_pin]['name'] == source_pin:
                    read_payload = [6,input_pin<<6,0]
                    #print "Reading payload %d : %s" % (input_pin, read_payload)
                    reading = self.spi.xfer2(read_payload)
                    result = (reading[1] << 8 | reading[2]) 
                    #print "Reading from %d : %s" % (input_pin, result)
                    return result 
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
            if int(pin_id) > 3 :
                raise Exception("Pin ID greater than 3 supplied, pin ids are zero referenced.")    
            
        except ValueError:
            raise Exception("Non integer Register or Pin ID supplied.")
        
        for input_pin in self.inputs:
            if self.inputs[input_pin]['name'] == pin_name:
                raise Exception("Pin Name %s is already in use on pin : %d " % (pin_name, input_pin))
        else:
            self.inputs[pin_id]['name'] = pin_name
                
