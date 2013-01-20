import sys
import smbus

import spidev
from Adafruit_I2C import Adafruit_I2C

from pigredients.ics import mma7660 as mma7660
from pigredients.ics import mag3110 as mag3110

_pixi_i2c_address = 0x70

_leds_out_register = 0x30 # 16bits, 2bits per led. 00 = off, 01 = slow blink, 10 = fast blink, 11 = on
_leds_config_register = 0x31 # 4bits, Always set to 0000 , we'll worry about other modes later.

_switch_in_register = 0x32 # 8bits, 2bits per switch, first bit current state, second bit 1 if state change since last read, automatically resets on read.

_valid_led_ids = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8']
_valid_led_ids.reverse()
_valid_led_state = {'on' : '11', 'off' : '00', 'slow' : '01', 'fast' : '10'}

class response_object(object):
    def __init__(self):
        self.success = False
        self.response = ""
        
    def __nonzero__(self):
        return self.success

    def __str__(self):
        return str(self.__dict__)

class PIXI200(object):
    def __init__(self, spi_address_hardware=0, spi_address_output=0, i2c_bus=0, i2c_address=_pixi_i2c_address, debug=False):
        self.debug = debug
        # setup spi comms
        self.spi = spidev.SpiDev()
        self.spi.open(spi_address_hardware, spi_address_output)
        # setup i2c comms
        self.i2c_bus = i2c_bus
        self._bus = smbus.SMBus(self.i2c_bus)
        # i2c bus for comms with the fpga
        self.i2c = Adafruit_I2C(i2c_address, bus=self._bus, debug=self.debug)
        # setup for accelerometers and magnatometers
        self.accel = mma7660.MMA7660(i2c_bus=self.i2c_bus, debug=self.debug)
        self.compass = mag3110.MAG3110(i2c_bus=self.i2c_bus, debug=self.debug)

        self._led_state = {}
        for led in _valid_led_ids:
            self._led_state[led] = 00        
        # set our led mode to 0000, this may be the default.
        self.set_led_mode(0000)

    def _spi_write(self, register_address, data):
        if data is not list or len(data) != 2:
            raise Exception("Spi write data should be in the form of list containing 2 bytes.")
        response = response_object()
        addresses_list = [register_address, 0x40]
        response.response = self.spi.xfer2(addresses_list + data)
        if response.response[0] == 0x30:
            response.success = True
        return response
    
    def _spi_read(self, register_address):
        response = response_object()
        # two bytes of zereos to request two bytes of data back.
        addresses_list = [register_address, 0x80, 0x00, 0x00]
        response.response = self.spi.xfer2(addresses_list)
        if response.response[0] == register_address:
            response.success = True
        return response
    

    def _i2c_write(self, register_address, data):
        return None
    
    def _i2c_read(self, register_address):
        return None

    def get_switch(self):
        switch_state = {'s1' : {'now' : None, 'pressed' : None}, 's2' : {'now' : None, 'pressed' : None}, 's3' : {'now' : None, 'pressed' : None}, 's4' : {'now' : None, 'pressed' : None}}
        read_buffer = bin(self._spi_read(_switch_in_register).response[3])[2:].zfill(8)
        switch_state['s1']['now'] = bool(int(read_buffer[7]))
        switch_state['s1']['pressed'] = bool(int(read_buffer[6]))
        switch_state['s2']['now'] = bool(int(read_buffer[5]))
        switch_state['s2']['pressed'] = bool(int(read_buffer[4]))
        switch_state['s3']['now'] = bool(int(read_buffer[3]))
        switch_state['s3']['pressed'] = bool(int(read_buffer[2]))
        switch_state['s4']['now'] = bool(int(read_buffer[1]))
        switch_state['s4']['pressed'] = bool(int(read_buffer[0]))
        return switch_state

    def get_buttons(self):
        return self.get_switch()
        
    def set_led_mode(self, led_mode):
        try :
            # null op
            int(led_mode)
            # not sure if this will work, as a 4bit register.
            response = self.spi.xfer2([_leds_config_register, 0x40, led_mode, 0])
            #print "led set mode got the response : %s" % response
        except TypeError:
            raise Exception('Invalid led mode requested, valid modes are 0000, 0001, 0010, 0011 etc.')

    def set_led(self, led_id, state):
        if led_id not in _valid_led_ids:
            raise Exception("Invalid led id given, valid led ids are : %s " % _valid_led_ids)
        if state not in _valid_led_state:
            raise Exception("Invalid led state given, valid led states are : %s " % _valid_led_state)
        self._led_state[led_id] = _valid_led_state[state]

    def set_on(self):
        for led_id in self._led_state:
            self._led_state[led_id] = _valid_led_state['on']

    def set_off(self):
        for led_id in self._led_state:
            self._led_state[led_id] = _valid_led_state['off']

    def update_leds(self):
        # flush the current led set states to the register.
        data_list = [_leds_out_register,0x40]
        temp_string = ""
        for led in _valid_led_ids:
            #print "Processing led : %s" % led
            temp_string = "%s%s" % (temp_string, self._led_state[led])
            #print "temp_string : %s " % temp_string
            if len(temp_string) == 8:
                #print "Temp string contains : %s" % temp_string
                data_list.append(int(temp_string, 2))
                temp_string = ""

        #print "data list contains : %s" % data_list
        response = self.spi.xfer2(data_list)
        #print "led set got the response : %s" % response
        
