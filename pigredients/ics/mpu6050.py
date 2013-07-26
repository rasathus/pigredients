import sys

import smbus
import math

from Adafruit_I2C import Adafruit_I2C

from pigredients.core.bitman import BitSequence

_mpu6050_address = 0x69
_mpu6050_clock_pll_xgyro = 0x01

_mpu6050_gyro_fs_250 = 0x00
_mpu6050_gyro_fs_500 = 0x01
_mpu6050_gyro_fs_1000 = 0x02
_mpu6050_gyro_fs_2000 = 0x03

_mpu6050_accel_fs_2 = 0x00
_mpu6050_accel_fs_4 = 0x01
_mpu6050_accel_fs_8 = 0x02
_mpu6050_accel_fs_16 = 0x03

_mpu6050_ra_pwr_mgmt_1 = 0x6b
_mpu6050_pwr1_clksel_bit = 2
_mpu6050_pwr1_clksel_length = 3

_mpu6050_ra_gyro_config = 0x1b
_mpu6050_gconfig_fs_sel_bit = 4
_mpu6050_gconfig_fs_sel_length = 2

_mpu6050_ra_accel_config = 0x1c
_mpu6050_aconfig_afs_sel_bit = 4
_mpu6050_aconfig_afs_sel_length = 2

_mpu6050_ra_pwr_mgmt_1 = 0x6b
_mpu6050_pwr1_sleep_bit = 6

_mpu6050_ra_accel_xout_h = 0x3b

_mpu6050_pwr1_device_reset_bit = 7

_mpu6050_config = 0x1a

_mpu6050_filter20hz = 4

class MPU6050(object):
    
    def __init__(self, i2c_bus=None, i2c_address=_mpu6050_address, debug=False):
                
        self.debug = debug
        # Create our i2c connection
        if i2c_bus is None:
            self.i2c = Adafruit_I2C(i2c_address, debug=self.debug)
        else:
            self._bus = smbus.SMBus(i2c_bus) 
            self.i2c = Adafruit_I2C(i2c_address, bus=self._bus, debug=self.debug)
    
    
        #self.set_clock_source(_mpu6050_clock_pll_xgyro)
        # set pwr management 1 byte for no sleep and x-axis gyro clock source.
        self.i2c.write8(_mpu6050_ra_pwr_mgmt_1, 0b00000001 )

        self.set_filtering(_mpu6050_filter20hz)

        self.set_gyro_range(_mpu6050_gyro_fs_250)
        self.set_accel_range(_mpu6050_accel_fs_2)
        self.sleep_mode(False)

    def _read_set_write(self, register, bit, val):
        reg_byte = BitSequence(self.i2c.readU8(register))
        reg_byte[bit] = val
        self.i2c.write8(register, reg_byte)
    
    def set_clock_source(self, source):
        pass
        #self.i2c.writeList(_mpu6050_ra_pwr_mgmt_1, [_mpu6050_pwr1_clksel_bit, _mpu6050_pwr1_clksel_length, source])

    def set_gyro_range(self, fs_sel):
        # set via 2 bits @ bit 3-4 in gyro_config register.
        reg_byte = BitSequence(self.i2c.readU8(_mpu6050_ra_gyro_config))
        print "Before Byte : %s" % reg_byte
        fs_sel_code = BitSequence(fs_sel)
        for bit in fs_sel_code:
            reg_byte[bit+3] = fs_sel_code[bit]
        print "After Byte : %s" % reg_byte
        self.i2c.write8(_mpu6050_ra_gyro_config, reg_byte)
        
    def set_accel_range(self, afs_sel):
        # set via 2 bits @ bit 3-4 in gyro_config register.
        reg_byte = BitSequence(self.i2c.readU8(_mpu6050_ra_accel_config))
        print "Before Byte : %s" % reg_byte
        afs_sel_code = BitSequence(afs_sel)
        for bit in afs_sel_code:
            reg_byte[bit+3] = afs_sel_code[bit]
        print "After Byte : %s" % reg_byte
        self.i2c.write8(_mpu6050_ra_accel_config, reg_byte)  
 
    def set_filtering(self, dlpf_cfg):
        # set via first 3 bits in config register.
        reg_byte = BitSequence(self.i2c.readU8(_mpu6050_config))
        print "Before Byte : %s" % reg_byte
        dlpf_code = BitSequence(dlpf_cfg)
        for bit in dlpf_code:
            reg_byte[bit] = dlpf_code[bit]
        print "After Byte : %s" % reg_byte
        self.i2c.write8(_mpu6050_config, reg_byte)
    
    def sleep_mode(self, mode):
        reg_byte = BitSequence(self.i2c.readU8(_mpu6050_ra_pwr_mgmt_1))
        print "Before Byte : %s" % reg_byte
        reg_byte[_mpu6050_pwr1_sleep_bit] = mode
        print "After Byte : %s" % reg_byte
        self.i2c.write8(_mpu6050_ra_pwr_mgmt_1, reg_byte)

    def reset(self):
        reg_byte = BitSequence(self.i2c.readU8(_mpu6050_ra_pwr_mgmt_1))
        print "Before Byte : %s" % reg_byte
        reg_byte[_mpu6050_pwr1_device_reset_bit] = True
        print "After Byte : %s" % reg_byte
        self.i2c.write8(_mpu6050_ra_pwr_mgmt_1, reg_byte)
        


    def get_accel(self):
        result = { 'x' : None, 'y' : None, 'z' : None }
        # clear the buffer
        read_buffer = self.i2c.readList(_mpu6050_ra_accel_xout_h, 6)
        # Process two's compliment values ...
        result['x'] = BitSequence((read_buffer[0] << 8) | read_buffer[1]).twos_complement()
        result['z'] = BitSequence((read_buffer[2] << 8) | read_buffer[3]).twos_complement()
        result['y'] = BitSequence((read_buffer[4] << 8) | read_buffer[5]).twos_complement()
        
        self.last_accel_result = result
        return result
