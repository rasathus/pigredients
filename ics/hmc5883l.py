import sys

import smbus

from Adafruit_I2C import Adafruit_I2C

i2c_address = 0x1e
write_reg = 0x3c
read_reg = 0x3d

# < Arduino Vars > 
HMC5883L_Address = 0x1E
ConfigurationRegisterA = 0x00
ConfigurationRegisterB = 0x01
ModeRegister = 0x02
DataRegisterBegin = 0x03

# </Arduino Vars >

_mode_register = 0x02
_mode_map = {    'continuous' : 0x00,
                'single' : 0x01,
                'idle' : 0x03}
_configuration_reg_b = 0x01



class HMC5883L(object):
    
    def __init__(self, i2c_bus=0, i2c_address=0x1e, debug=False):
                
        self.debug = debug
        self.gauss = 0.88
        self.scale = 0x00
        self._multiplication_factor = 0.73
        # Create our i2c connection
        self._bus = smbus.SMBus(i2c_bus) 
        self.i2c = Adafruit_I2C(i2c_address, bus=self._bus, debug=self.debug)
        
        # set our compass to continuous mode.
        self.set_mode('continuous')

    def set_mode(self, mode):
        if mode.lower() in _mode_map:
            self.i2c.write8(_mode_register, _mode_map[mode.lower()])
        else:
            raise Exception('Invalid mode requested, valid modes are continuous, single and idle.')
        
    def get_value(self):
        result = { 'x' : None, 'y' : None, 'z' : None }
        # clear the buffer
        read_buffer = self.i2c.readList(DataRegisterBegin, 6)
        
        result['x'] = round(((read_buffer[0] << 8) | read_buffer[1]) * self._multiplication_factor , 3)
        result['z'] = round(((read_buffer[2] << 8) | read_buffer[3]) * self._multiplication_factor , 3)
        result['y'] = round(((read_buffer[4] << 8) | read_buffer[5]) * self._multiplication_factor , 3)
        
        self.last_result = result
        return result

    def set_scale(self, gauss):
        if gauss == 0.88:
            self.gauss = gauss
            self.scale = 0x00
            self._multiplication_factor = 0.73
        elif gauss == 1.3:
            self.gauss = gauss
            self.scale = 0x01
            self._multiplication_factor = 0.92
        elif gauss == 1.9:
            self.gauss = gauss
            self.scale = 0x02
            self._multiplication_factor = 1.22
        elif gauss == 2.5:
            self.gauss = gauss
            self.scale = 0x03
            self._multiplication_factor = 1.52
        elif gauss == 4.0:
            self.gauss = gauss
            self.scale = 0x04
            self._multiplication_factor = 2.27
        elif gauss == 4.7:
            self.gauss = gauss
            self.scale = 0x05
            self._multiplication_factor = 2.56
        elif gauss == 5.6:
            self.gauss = gauss
            self.scale = 0x06
            self._multiplication_factor = 3.03
        elif gauss == 8.1:
            self.gauss = gauss
            self.scale = 0x07
            self._multiplication_factor = 4.35
        else:
            raise Exception("Invalid gauss value, valid gauss values are 0.88, 1.3, 1.9, 2.5, 4.0, 4.7, 5.6 or 8.1")

    	# Setting is in the top 3 bits of the register.
    	self.scale = self.scale << 5
        self.i2c.write8(_configuration_reg_b, self.scale)
        
    def get_scale(self):
        return self.scale
