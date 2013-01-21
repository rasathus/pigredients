#!/usr/bin/env python
# - * - Coding: utf-8 - * -

import random
import datetime
import subprocess

from time import sleep
from pigredients.displays import textStarSerialLCD as textStarSerialLCD

display = None

def write_datetime():
    display.position_cursor(1, 1)
    dt=str(datetime.datetime.now())
    display.ser.write('   '+dt[:10]+'   '+'    '+dt[11:19]+'    ')

def get_addr(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return '?.?.?.?'

def write_ip_addresses():
    display.position_cursor(1, 1)
    display.ser.write('e'+get_addr('eth0').rjust(15)+'w'+get_addr('wlan0').rjust(15))

def write_distance():
    display.position_cursor(1, 1)
    r = []
    for i in range (0,10):
        r.append(adc_instance.read_input(0))
    a = sum(r)/10.0
    v = (a/1023.0)*3.3
    d = 16.2537 * v**4 - 129.893 * v**3 + 382.268 * v**2 - 512.611 * v + 306.439
    cm = int(round(d))
    val = '%d cm' % cm
    percent = int(cm/1.5)
    display.ser.write(str(val).ljust(16))
    display.capped_bar(16, percent)

def write_rover_state():
    display.position_cursor(1, 1)
    left_track = random.randrange(0, 100)
    right_track = random.randrange(0, 100)
    display.ser.write("FL "+chr(254)+"b"+chr(4)+chr(left_track)+" FR "+chr(254)+"b"+chr(4)+chr(right_track)+" ")
    display.ser.write("RL "+chr(254)+"b"+chr(4)+chr(left_track)+" RR "+chr(254)+"b"+chr(4)+chr(right_track)+" ")

# Callbacks
def on_page():
    display.clear()
    display.window_home()
    if display.page == 'a':
        write_rover_state()
    elif display.page == 'b':
        write_datetime()
    elif displayipage == 'c':
        # IP Page
        write_ip_addresses()
    elif display.page == 'd':
        write_datetime()

def on_poll():
    if display.page == 'a':
        write_rover_state()
    #elif display.page == 'c':
    #    display.scroll_down()

def on_tick():
    if display.page == 'b':
        write_datetime()
    elif display.page == 'd':
        write_datetime()

def on_refresh():
    if display.page == 'a':
        write_rover_state()
    elif display.page == 'b':
        write_datetime()
    elif display.page == 'c':
        write_ip_addresses()
    elif display.page == 'd':
        write_datetime()



display = textStarSerialLCD.Display(on_page, on_poll, on_tick, on_refresh, baud_rate=115200)

# Depending on the applicaiton, we could use the non blocking threaded_run method, or the blocking run method, if all code is enclosed within the page implementations.

display.run()











































import serial
from threading import Thread

class Display():
    """ Manages the 16x2 4 button display:
        on_tick called every 0.1 seconds as part of the main loop after the button read
        on_poll called every 1.5 seconds
        on_page called when a new page has been selected
        on_refresh called every 30 seconds"""
    def __init__(self,on_page=None,on_poll=None,on_tick=None,on_refresh=None,char_clear=chr(12),
        char_esc=chr(254),char_block=chr(154),ticks_poll=15,ticks_refresh=300,baud_rate=115200,tty_path='/dev/ttyAMA0'):
        # Start the serial port
        self.ser = serial.Serial(tty_path,baud_rate,timeout=0.1)
        # Callbacks
        self.on_page = on_page
        self.on_poll = on_poll
        self.on_tick = on_tick
        self.on_refresh = on_refresh

        self.char_esc = char_esc
        self.char_clear = char_clear
        self.char_block = char_block
        
        self.page = 'a'
        self.poll = ticks_poll
        self.poll_max = ticks_poll
        self.refresh = ticks_refresh
        self.refresh_max = ticks_refresh
        
        self._run = True

    def position_cursor(self,line,column):
        self.ser.write(self.char_esc+'P'+chr(line)+chr(column))
    
    def scroll_down(self):
        self.ser.write(self.char_esc+'O'+chr(0))
    
    def window_home(self):
        self.ser.write(self.char_esc+'G'+chr(1))
        
    def capped_bar(self, length, percent):
        self.ser.write(self.char_esc+'b'+chr(length)+chr(percent))
        
    def clear(self):
        self.ser.write(self.char_clear)

    def run(self):
        #show initial page
        self.ser.write('  Starting....  ')
        if self.on_page != None:
            self.on_page()
        #main loop
        while self._run:
            key = str(self.ser.read(1))
            if key != '' and key in 'abcd':
                self.page = key
                self.refresh = self.refresh_max
                self.poll = self.poll_max
                if self.on_page != None:
                    self.on_page()
            else:
                self.refresh-=1
                if self.refresh == 0:
                    self.refresh = self.refresh_max
                    if self.on_refresh != None:
                        self.on_refresh()
                        
                self.poll-=1
                if self.poll == 0:
                    self.poll = self.poll_max
                    if self.on_poll != None:
                        self.on_poll()
                        
                if self.on_tick != None:
                    self.on_tick()
                    
    def threaded_run(self):
        self.threaded_runner = Thread(target=self.run)
        self.threaded_runner.start()

    def stop(self):
        print "Display stop called"
        self._run = False
