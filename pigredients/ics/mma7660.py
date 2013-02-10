import sys
import smbus
import time
import math

from Adafruit_I2C import Adafruit_I2C

_mma7660_address = 0x4c
_x_register = 0x00
_y_register = 0x01
_z_register = 0x02
_tilt_register = 0x03
_sleepcount_register = 0x05
_interupt_register = 0x06
_mode_register = 0x07
_sr_register = 0x08

# hardcoded for now, but will open up to configuration later
interupt_configuration = 0x10
sr_configuration = 0x00
sr_configuration = 0x40 
sr_configuration = 0xe8 # 11101000 Heavily filtered values, 8 measurement matched. 16 samples sleep, 120 samples wake. 

mode_configuration_inactive = 0x00 
mode_configuration_active = 0x19 # 00011001


class MMA7660(object):
    def __init__(self, i2c_bus=None, i2c_address=_mma7660_address, debug=False):
            
        self.debug = debug
        # Create our i2c connection
        if i2c_bus is None:
            self.i2c = Adafruit_I2C(i2c_address, debug=self.debug)
        else:
            self._bus = smbus.SMBus(i2c_bus) 
            self.i2c = Adafruit_I2C(i2c_address, bus=self._bus, debug=self.debug)
        
        # set our interupt configuration.
        self.set_register(_interupt_register, interupt_configuration)
        
        # set sr register to autowake, and 120 samples to enable tap etc.
        self.set_register(_sr_register, sr_configuration)
        
        self.last_result = None
        # Pause to wait for a solid fix as were using lots of filtering.
        time.sleep(0.05)

    def read_register(self, address=None):
        # Due to the ic requiring 'repeated start', temporarily all reads are done by reading all registers required every time any value is requested.  Need to find a better solution to this.    
        register_state = self.i2c.readList(0x00, 9)
        # print "Registers read as : %s" % register_state
        if address is None:
            return register_state
        else:
            # assume address is an int, only requires single response
            return register_state[int(address)]

    def go_standby(self):
        self.i2c.write8(_mode_register, mode_configuration_inactive)
        current_mode = self.read_register(_mode_register)
        while current_mode > 0 :
            # print "Not gone into standby yet, trying again ..."
            self.i2c.write8(_mode_register, mode_configuration_inactive)
            time.sleep(0.05) 
            current_mode = self.read_register(_mode_register)
        return True
        
    def go_active(self):
        self.i2c.write8(_mode_register, mode_configuration_active)
        current_mode = self.read_register(_mode_register)
        while current_mode < 1:
            # print "Mode register still in standby, trying again ..."
            self.i2c.write8(_mode_register, mode_configuration_active)
            time.sleep(0.05)
            current_mode = self.read_register(_mode_register)
        return True

    def get_sleepcount(self):
        return self.i2c.readU8(_sleepcount_register)

    def set_register(self, register_address, register_data):
        # print "Mode register pre standby : %s" % bin(self.read_register(_mode_register))[2:].zfill(8)
        self.go_standby()
        # print "Mode register post standby : %s" % bin(self.read_register(_mode_register))[2:].zfill(8)
        time.sleep(0.05)
        # print "Setting register %s to %s" % (hex(register_address), bin(register_data)[2:].zfill(8))
        self.i2c.write8(register_address, register_data)
        time.sleep(0.05)
        current_register_contents = self.read_register(register_address)
        
        while current_register_contents != register_data:
            # print "current : %s does not match intended : %s , trying again ..." % (current_register_contents , register_data)
            self.i2c.write8(register_address, register_data)
            time.sleep(0.05)  
            current_register_contents = self.read_register(register_address)              
        
        # print "Register %s now set to %s" % (hex(register_address), bin(self.read_register(register_address))[2:].zfill(8))
        # print "Mode register pre active : %s" % bin(self.read_register(_mode_register))[2:].zfill(8)
        self.go_active()
        # print "Mode register post active : %s" % bin(self.read_register(_mode_register))[2:].zfill(8)
        
    def get_value(self):
        result = { 'x' : None, 'y' : None, 'z' : None }
        # print "Mode register byte : %s" % bin(self.read_register(_mode_register))[2:].zfill(8)
        # print "SR register byte : %s" % bin(self.read_register(_sr_register))[2:].zfill(8)
        # Read 3 bytes in the form of x-out, y-out, z-out
    	# The mma7660 uses bits 0:5 to represent the output and the bit 6 to represent an alert.  In case of an alert, the register was read as it was written to this value should be ignored and re-read.            
    	result['x'] = self.read_register(_x_register)
    	while result['x'] >= 64:
    	    # retry our read until we get one without an alert bit.   
    	    #print "Got an alert bit in x byte : %s" % bin(result['x'])
            result['x'] = self.read_register(_x_register)

        # print "got in x byte : %s" % bin(result['x'])[2:].zfill(8)    	
        """
        if result['x'] >= 32:
            # axis is negative
            result['x'] = 0 - (result['x'] -32)
        """

        result['y'] = self.read_register(_y_register)
        while result['y'] >= 64:
            # retry our read until we get one without an alert bit.
            #print "Got an alert bit in y byte : %s" % bin(result['y'])
            result['y'] = self.read_register(_y_register)
        
        # print "got in y byte : %s" % bin(result['y'])[2:].zfill(8)
        """
        if result['y'] >= 32:
            # axis is negative
            result['y'] = 0 - (result['y'] -32)
        """
        result['z'] = self.read_register(_z_register)
        while result['z'] >= 64:
            # retry our read until we get one without an alert bit.
            #print "Got an alert bit in z byte : %s" % bin(result['z'])
            result['z'] = self.read_register(_z_register)
        
        # print "got in z byte : %s" % bin(result['z'])[2:].zfill(8)
        """
        if result['z'] >= 32:
            # axis is negative
            result['z'] = 0 - (result['z'] -32)
        """
        self.last_result = result
        return result

    def get_face(self):
        orientation = {'backfront' : None, 'portland' : None, 'tap' : None, 'shake' : None}
        tilt_reg = self.read_register(_tilt_register)
        while tilt_reg > 63:
	    #print "Alert flag for face orientation"
            tilt_reg = self.read_register(_tilt_register)

        print "Tilt Reg : %s" % bin(tilt_reg)[2:].zfill(8)


        back_front = "%s%s" % (tilt_reg&1, tilt_reg&0)
        if back_front == "01":
            orientation['backfront'] = 'Front'
        elif back_front == "10":
            orientation['backfront'] = 'Back'
        else :
            orientation['backfront'] = 'Unknown'
    
        port_land = "%s%s%s" % (tilt_reg&4, tilt_reg&3, tilt_reg&2)
        if port_land == "001":
            orientation['portland'] = 'Landscape Left'
        elif port_land == "010":
            orientation['portland'] = 'Landscape Right'
        elif port_land == "101":
            orientation['portland'] = 'Portrait Down'
        elif port_land == "110":
            orientation['portland'] = 'Portrait Up'
        else :
            orientation['portland'] = 'Unknown'

        if tilt_reg&5 == "1":
            orientation['tap'] = True
        else :
            orientation['tap'] = False

        if tilt_reg&7 == "1":
            orientation['shake'] = True
        else :
            orientation['shake'] = False

        #print "Tilt register contains : %s" % bin(tilt_reg)[2:].zfill(8)
        print orientation	
        return orientation
