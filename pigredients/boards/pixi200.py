# -*- coding: utf-8 -*-
import sys
import smbus
import time

import spidev
from Adafruit_I2C import Adafruit_I2C

from pigredients.ics import mma7660 as mma7660
from pigredients.ics import mag3110 as mag3110

_pixi_i2c_address = 0x70

_leds_out_register = 0x30 # 16bits, 2bits per led. 00 = off, 01 = slow blink, 10 = fast blink, 11 = on
_leds_config_register = 0x31 # 4bits, Always set to 0000 , we'll worry about other modes later.

_switch_in_register = 0x32 # 8bits, 2bits per switch, first bit current state, second bit 1 if state change since last read, automatically resets on read.

_display_write_register = 0x38 # 16bits 

_valid_led_ids = ['d1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8']
_valid_led_ids.reverse()
_valid_led_state = {'on' : '11', 'off' : '00', 'slow' : '01', 'fast' : '10'}
_valid_display_brightness = {100 : 0, 75 : 1, 50 : 2, 25 : 3}

_max_display_xcord = 39
_max_display_ycord = 1

class response_object(object):
    def __init__(self):
        self.success = False
        self.response = ""
        
    def __nonzero__(self):
        return self.success

    def __str__(self):
        return str(self.__dict__)

class PIXI200(object):
    def __init__(self, spi_address_hardware=0, spi_address_output=0, i2c_bus=0, i2c_address=_pixi_i2c_address, use_display=True, debug=False):
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
        if use_display:
            # initialised our display outputs on GPIO3
            self._init_display()

    def _spi_write(self, register_address, data):
        #if type(data) is not list or len(data) != 2:
        #    raise Exception("Spi write data should be in the form of list containing 2 bytes.")
        response = response_object()
        addresses_list = [register_address, 0x40]
        response.response = self.spi.xfer2(addresses_list + data)
        if self.debug:
            print "wrote : %s to register :%s" % (data, hex(register_address))

        if response.response[0] == register_address:
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
            raise Exception("Invalid led id given, valid led ids are : %s " % _valid_led_ids.keys())
        if state not in _valid_led_state:
            raise Exception("Invalid led state given, valid led states are : %s " % _valid_led_state.keys())
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


    def display_clear(self):
        response = self._spi_write(0x38, [0,1])

    def _init_display(self):
        # Setup our GPIO3 modes for display write
        response = self._spi_write(0x2c, [0x00,0x02])
        response = self._spi_write(0x2d, [0x00,0x02])
        self.display_clear()

    def _display_brightness(self, brightness):
        # UNFINISHED !!!!
        if brightness not in _valid_display_brightness:
            raise Exception("Invalid brightness given, valid states are : %s " % _valid_display_brightness.keys())

        response = self._spi_write(0x38, [0x02,_valid_display_brightness[brightness]])
        print "Sent brightness command to 0x38 : %s " % response

    def display_state(self, state):
        if state not in ['on','off']:
            raise Exception("Invalid display state given, valid states are 'on' or 'off'")

        if state == 'off':
            response = self._spi_write(0x38, [0,8])
        else:
            response = self._spi_write(0x38, [0,12])
        
        
    def _display_write(self, data):
        if type(data) is list:
            for element in data:
                response = self.spi.xfer2([_display_write_register,0x40, 0x02, element])            
        else:
            for char in data:
                data_list = [_display_write_register,0x40]
                data_list.append(0x02) # set our rs bit
                try:
                    data_list.append(ord(char))
                except ValueError:
                    # unknown char, using a placeholder instead.
                    data_list.append(0x3f) # insert a question mark instead.
                except TypeError:
                    # ord throws a type error if given something other than a string. if so check its an int and pass it along anyway, to allow us to send hex codes.
                    try:
                        data_list.append(int(char)) # send the value unprocessed
                    except ValueError:
                        # unknown char, using a placeholder instead.
                        data_list.append(0x3f) # insert a question mark instead.

                response = self.spi.xfer2(data_list)
        return response

    def display_write(self, data, x=0, y=0):
        # Setup our GPIO3 modes for display write
        if x > _max_display_xcord or y > _max_display_ycord :
            raise Exception("Invalid display coordinate given, x coordinates should be less than or equal to %d and y coordinates less than or equal to %d" % (_max_display_xcord, _max_display_ycord))
        # send our x,y curser start addresses
        cursor_pos = 128 + (y << 6) + x
        self._spi_write(0x38,[0x00, cursor_pos])
        # send our data to the display
        self._display_write(data)

    def display_bar_graph(self, x, y , length, percentage, reverse=False):
        try:
            if int(percentage) > 100 :
                raise ValueError
        except ValueError:
            raise Exception("Invalid percentage given, valid percentages are integers between 0 and 100")

        data_list = []
        filled_elements = int((((5.0 * length) / 100 ) * percentage))
        for element in range(length):
            if filled_elements >= 5:
                data_list.append(0x14)
                filled_elements = filled_elements - 5
            elif filled_elements == 4:
                if reverse:
                    data_list.append(0x15)    
                else:
                    data_list.append(0x13)
                filled_elements = filled_elements - 4
            elif filled_elements == 3:
                if reverse:
                    data_list.append(0x16)    
                else:
                    data_list.append(0x12)
                filled_elements = filled_elements - 3
            elif filled_elements == 2:
                if reverse:
                    data_list.append(0x17)    
                else:
                    data_list.append(0x11)
                filled_elements = filled_elements - 2
            elif filled_elements == 1:
                if reverse:
                    data_list.append(0x18)    
                else:
                    data_list.append(0x10)
                filled_elements = filled_elements - 1
            else:
                data_list.append(0x20)
                filled_elements = filled_elements - 0

        if reverse:
            data_list.reverse()
        self.display_write(data_list, x=x, y=y)

