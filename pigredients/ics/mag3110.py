import sys
import smbus
import time
import math

from Adafruit_I2C import Adafruit_I2C

_mag3110_address = 0x0e
_ctrl_register1 = 0x10
_ctrl_register2 = 0x11
_dr_status_register = 0x00
_sysmod_register = 0x08

_die_temp_register = 0x0F

_ctrl_register1_value = 0x01
_ctrl_register2_value = 0x80

# For opperation modes refer to table 31 of the freescale datasheet.
# operation modes are based on '10101' - output rate @ 1.25hz with 32 times oversampling and 34.4 ua current draw.
_operation_modes = {'continuous' : 170, # 
                    'single' : 169,
                    'standby' : 168}
_get_mode_map = {0: 'Standby', 1 : 'ActiveRaw', 2 : 'ActiveCorrected'}                
# it sounds as if the pointer moves for you after each byte read, so should be able to read 6 bytes starting at this register.
_first_read_register = 0x01

def fix_msb(val):
    if val >= 32768:
        val -= 65536
    return val

class MAG3110(object):
    
    def __init__(self, i2c_bus=None, i2c_address=_mag3110_address, declination_angle=0.0457, debug=False):
            
        self.debug = debug
        self.last_result = None
        self.declination_angle = declination_angle
        # Create our i2c connection
        if i2c_bus is None:
            self.i2c = Adafruit_I2C(i2c_address, debug=self.debug)
        else:
            self._bus = smbus.SMBus(i2c_bus) 
            self.i2c = Adafruit_I2C(i2c_address, bus=self._bus, debug=self.debug)

        # enable autoreset mode, not quite sure why but the arduino implementations do it.
        self.i2c.write8(_ctrl_register2, _ctrl_register2_value)
        time.sleep(0.015)
        current_register_contents = self.i2c.readU8(_ctrl_register2)
        if current_register_contents != _ctrl_register2_value:
            print "WARNING : Register contents mismatch !!"
        """
        while current_register_contents != _ctrl_register2_value:
            print "WARNING : Register contents mismatch !!"
            self.i2c.write8(_ctrl_register2, _ctrl_register2_value)
            time.sleep(0.015)
        """

        self.i2c.write8(_ctrl_register1, _ctrl_register1_value)
        time.sleep(0.015)
        current_register_contents = self.i2c.readU8(_ctrl_register1)
        if current_register_contents != _ctrl_register1_value:
            print "WARNING : Register contents mismatch !!"
        """
        while current_register_contents != _ctrl_register1_value:
            print "WARNING : Register contents mismatch !!"
            self.i2c.write8(_ctrl_register1, _ctrl_register1_value)
            time.sleep(0.015)
        """



        # set device to standby mode, before setting control registers.
        #current_sysmod = self.get_mode()
        
        # take device out of standby mode, prior to use.

        
        # set our compass to continuous mode.
        #self.set_mode('continuous')

    def get_mode(self):
        # will use later to abstract the complexities of table 31 from the user.
        self.i2c.readU8(_sysmod_register)
        return None
        
    def get_temp(self):
        return self.i2c.readS8(_die_temp_register)

    def set_mode(self, mode):
        # will use later to abstract the complexities of table 31 from the user.
        if mode.lower() in _mode_map:
            self.i2c.write8(_mode_register, _mode_map[mode.lower()])
        else:
            raise Exception('Invalid mode requested, valid modes are continuous, single and idle.')
            
    def get_value(self):
        result = { 'x' : None, 'y' : None, 'z' : None }

        # Read 6 bytes in the form of x-MSB, x-LSB, y-MSB, y-LSB, z-MSB, z-LSB
        read_buffer = self.i2c.readList(_first_read_register, 6)
        
        result['x'] = fix_msb((read_buffer[0] << 8) | read_buffer[1])
        result['y'] = fix_msb((read_buffer[2] << 8) | read_buffer[3])
        result['z'] = fix_msb((read_buffer[4] << 8) | read_buffer[5])
        
        self.last_result = result
        return result
        
    def get_heading(self):
        raw_data = self.get_value()
        heading = math.atan2(raw_data['y'], raw_data['x'])
        print "--Begining of Reading--"
        print "Heading pre correction : %f" % heading
        print "Heading Degrees pre correction : %f" % math.degrees(heading)
        
        heading += self.declination_angle

        print "Pre-corrected heading %s" % heading
        if heading < 0 :
            heading = heading + 2 * math.pi
        elif heading > 2 * math.pi:
            heading = heading - 2 * math.pi

        print "X Value : %f" % raw_data['x']
        print "Y Value : %f" % raw_data['y']        
        print "Radians : %f" % heading
        print "Degrees : %f" % math.degrees(heading)
        print "--End of Reading--"
        return math.degrees(heading)        
