'''
@author: Jeremy Blythe

Modularised and extended by Chris Fane

textStarSerialLCD - Manages the Textstar 16x2 4 button display

Read the blog entry at http://jeremyblythe.blogspot.com for more information
'''

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
