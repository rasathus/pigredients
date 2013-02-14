import spidev
import time
import random

# All set commands set the state only, and so require a write command to be displayed.
		
class LPD6803_Chain(object):
	
    def __init__(self, ics_in_chain=25, spi_address_hardware=0, spi_address_output=0):
		# default to 25 ics in the chain, so it works with no params with the Adafruit RGB LED Pixels - http://www.adafruit.com/products/738
        self.number_of_ics = ics_in_chain
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        self.ics = {}
        
        for ic in range(self.number_of_ics):
            self.ics[ic] = { 'R' : 0 , 'G' : 0, 'B' : 0, 'lumi' : 0 }
        
		#Write out the current zero'd state to the chain.
        self.write()       

    def two_byte_pack(self, rgb_dict):
        # take in our RGB values in the form of 1 int per component, and transform to 2 bytes in the structure of ...
        # 1<5 bits Red><5 bits Green><5 Bits Blue>
        return_bytes = bytearray(2)
        # creating 16bits to allow us to bitshift values into place.
        temp_16bit = 0b0000000000000000
        # Set our most significant bit to on.
        temp_16bit += 32768

        # take 5 most significant bits from each component, by shifting 3 pos to the right.  Then shift into their appropriate place.
        temp_16bit |= (rgb_dict['R'] >>3) << 10  # Red into bits 11-15
        temp_16bit |= (rgb_dict['G'] >>3) << 5  # Green into bits 6-10
        temp_16bit |= (rgb_dict['B'] >>3)  # Blue into bits 1-5

        #return_bytes initialised as zeros, going to mask the bits were interested in, and then bitshift the values to acces the bits we need.
        return_bytes[0] = (temp_16bit & 0xFF00) >> 8
        return_bytes[1] = (temp_16bit & 0x00FF) >> 0
            
        return return_bytes

    def write(self):
        # Iterate through our IC states, and write out 2 bytes for each, representing 1<5 bits Red><5 bits Green><5 Bits Blue>
        # pre charging our output bytes with 32bit start frame.
        byte_list = []
        # write out our 32bit start frame
        self.spi.xfer2([0,0,0,0])
        for ic in self.ics:
            byte_pair = self.two_byte_pack(self.ics[ic])
            byte_list.append(byte_pair[0])
            byte_list.append(byte_pair[1])
        
        self.spi.xfer2(byte_list)
        # send out 'append pulse', one for each pixel.
        append_pulses = []
        for ic in self.ics:
            append_pulses.append(0)
        self.spi.xfer2(append_pulses)
        
        
    def set(self):
        # Alias of write
        return self.write()

    def print_ics(self):
        print self.ics
                
    def set_ic(self, ic_id, rgb_value=[], lumi=100):
		# if not given a luminance value, default to 100%
        # Check we've been given a valid rgb_value.
        if ic_id > self.number_of_ics -1:
            raise Exception("Invalid ic_id : ic_id given is greater than the number number of ics in the chain.")
            
        if len(rgb_value) < 3:
            raise Exception("Invalid rgb_value : %s , for pin : %s, please pass a list containing three state values eg. [255,255,255]" % (rgb_value, ic_id))
       
        try:
			# Null op to ensure we've been given an integer.
            int(ic_id)
            self.ics[ic_id]= {'R' : rgb_value[0], 'G' : rgb_value[1], 'B' : rgb_value[2], 'lumi' : lumi} 
        except ValueError:
            raise Exception("Pin number is not a valid integer.")    
                    
    def set_rgb(self, rgb_value, lumi=100):
        if len(rgb_value) != 3:
            raise Exception("Invalid rgb_value: %s, please pass a list containing three state values eg. [255,255,255]" % rgb_value)
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : rgb_value[0], 'G' : rgb_value[1], 'B' : rgb_value[2], 'lumi' : lumi}
 
            
    def all_on(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        # write out our 32bit start frame
        self.spi.xfer2([0,0,0,0])
        for ic in self.ics:
            byte_pair = self.two_byte_pack({'R' : 255, 'G' : 255, 'B' : 255})
            byte_list.append(byte_pair[0])
            byte_list.append(byte_pair[1])
        
        self.spi.xfer2(byte_list)
        # send out 'append pulse', one for each pixel.
        append_pulses = []
        for ic in self.ics:
            append_pulses.append(0)
        self.spi.xfer2(append_pulses)

    def all_off(self):
        # !! NOTE !!
        # This does not affect pin state
        byte_list = []
        # write out our 32bit start frame
        self.spi.xfer2([0,0,0,0])
        for ic in self.ics:
            byte_pair = self.two_byte_pack({'R' : 0, 'G' : 0, 'B' : 0})
            byte_list.append(byte_pair[0])
            byte_list.append(byte_pair[1])

        self.spi.xfer2(byte_list)
        # send out 'append pulse', one for each pixel.
        append_pulses = []
        for ic in self.ics:
            append_pulses.append(0)
        self.spi.xfer2(append_pulses)
        
    def set_white(self, lumi=100):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 255, 'G' : 255, 'B' : 255, 'lumi' : lumi}

    def set_red(self, lumi=100):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 255, 'G' : 0, 'B' : 0, 'lumi' : lumi}
             
    def set_green(self, lumi=100):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 255, 'B' : 0, 'lumi' : lumi}
                          
    def set_blue(self, lumi=100):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 0, 'B' : 255, 'lumi' : lumi}
                     
    def set_off(self):
        for ic in range(self.number_of_ics):
             self.ics[ic] = {'R' : 0, 'G' : 0, 'B' : 0, 'lumi' : 0}

    def all_random(self):
        byte_list = []
        # write out our 32bit start frame
        self.spi.xfer2([0,0,0,0])
        for ic in range(self.number_of_ics):
            byte_pair = self.two_byte_pack({'R' : random.randint(0,255), 'G' : random.randint(0,255), 'B' : random.randint(0,255)})
            byte_list.append(byte_pair[0])
            byte_list.append(byte_pair[1])
        
        self.spi.xfer2(byte_list)
        # send out 'append pulse', one for each pixel.
        append_pulses = []
        for ic in self.ics:
            append_pulses.append(0)
        self.spi.xfer2(append_pulses)

    def cycle(self, delay=0.01):
        inc_vals = {}
        for ic in range(self.number_of_ics):
            inc_vals[ic] = {'R' : True, 'G' : True, 'B' : True}
            self.ics[ic]['R'] = random.randint(0,255)
            self.ics[ic]['G'] = random.randint(0,255)
            self.ics[ic]['B'] = random.randint(0,255)
            self.ics[ic]['lumi'] = 100
                    
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
        