import spidev
import time
import random

# All set commands set the state only, and so require a write command to be displayed.
		
class LPD8806_Chain(object):
	
    def __init__(self, ics_in_chain=32, spi_address_hardware=0, spi_address_output=0):
        # default to 32 ics in the chain, equating to 1 metre
        self.number_of_ics = ics_in_chain
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        self.ics = {}
        
        for ic in range(self.number_of_ics):
            self.ics[ic] = { 'R' : 0 , 'G' : 0, 'B' : 0}
        
        #Write out the current zero'd state to the chain.
        self.write()       
		
    def write(self):
        # Iterate through our IC states, and write out 3 bytes for each, representing <Red Byte><Green Byte><Blue Byte>
        byte_list = []
        for ic in self.ics:
            # Append our colour bytes to the output list. Using order GRB
            byte_list.append(0x80 | (int(self.ics[ic]['G']) >> 1))
            byte_list.append(0x80 | (int(self.ics[ic]['R']) >> 1))
            byte_list.append(0x80 | (int(self.ics[ic]['B']) >> 1))
        #LPD8806 Chipset requires an extra 0x00 per meter to push things along, according to the Arduino Library from adafruit.
        for extra in range(self.number_of_ics//32):
            byte_list.append(0x00)
        self.spi.xfer2(byte_list)
        # Clock in our latch.
        self.spi.xfer2([0x00,0x00,0x00])

        
    def set(self):
        # Alias of write
        return self.write()

    def print_ics(self):
        print self.ics
                
    def set_ic(self, ic_id, rgb_value=[]):
        # Check we've been given a valid rgb_value.
        if ic_id > self.number_of_ics -1:
            raise Exception("Invalid ic_id : ic_id given is greater than the number number of ics in the chain.")
            
        if len(rgb_value) < 3:
            raise Exception("Invalid rgb_value : %s , for pin : %s, please pass a list containing three state values eg. [255,255,255]" % (rgb_value, ic_id))
       
        try:
			# Null op to ensure we've been given an integer.
            int(ic_id)
            self.ics[ic_id]= {'R' : rgb_value[0], 'G' : rgb_value[1], 'B' : rgb_value[2]}
        except ValueError:
            raise Exception("Pin number is not a valid integer.")    
                    
    def set_rgb(self, rgb_value):
        if len(rgb_value) != 3:
            raise Exception("Invalid rgb_value: %s, please pass a list containing three state values eg. [255,255,255]" % rgb_value)
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : rgb_value[0], 'G' : rgb_value[1], 'B' : rgb_value[2]}
 
            
    def all_on(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for ic in range(self.number_of_ics):
            byte_list.append(255)
            byte_list.append(255)
            byte_list.append(255)
        self.spi.xfer2(byte_list)       
        # Clock in our latch.
        self.spi.xfer2([0x00,0x00,0x00,0x00])
 
    def all_off(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        for ic in range(self.number_of_ics):
            byte_list.append(0)
            byte_list.append(0)
            byte_list.append(0)
        self.spi.xfer2(byte_list)
        # Clock in our latch.
        self.spi.xfer2([0x00,0x00,0x00,0x00])

    def set_white(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 255, 'G' : 255, 'B' : 255}

    def set_red(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 255, 'G' : 0, 'B' : 0}
             
    def set_green(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 255, 'B' : 0}
                          
    def set_blue(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 0, 'B' : 255}
                     
    def set_off(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 0, 'B' : 0}

    def all_random(self):
        byte_list =[]
        for ic in range(self.number_of_ics):
            byte_list.append(random.randint(0,255))
            byte_list.append(random.randint(0,255))
            byte_list.append(random.randint(0,255))

        self.spi.xfer2(byte_list)   
        # Clock in our latch.
        self.spi.xfer2([0x00,0x00,0x00,0x00])

    def cycle(self, delay=0.01):
        inc_vals = {}
        for ic in range(self.number_of_ics):
            inc_vals[ic] = {'R' : True, 'G' : True, 'B' : True}
            self.ics[ic]['R'] = random.randint(0,255)
            self.ics[ic]['G'] = random.randint(0,255)
            self.ics[ic]['B'] = random.randint(0,255)
                    
        for i in range(512):            
            for ic in range(self.number_of_ics):
                for val in ['R','G','B']:
                    if self.ics[ic][val] >= 255:
                        inc_vals[ic] = False
                    elif self.ics[ic][val] <= 0:
                        inc_vals[ic] = True
                                            
                    if inc_vals[ic] == True :
                        self.ics[ic][val] = self.ics[ic][val] + 5
                    else :
                        self.ics[ic][val] = self.ics[ic][val] - 5
                    
            self.write()
            time.sleep(delay)
        
