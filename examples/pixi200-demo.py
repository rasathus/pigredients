import datetime
import time
import subprocess

from random import randint
from threading import Thread

from pigredients.boards import pixi200 as pixi200


pixi = pixi200.PIXI200(display_mode='vfd', display_width=40, display_height=2, debug=False)
_display_write_register = 0x38 # 16bits 
perc_const = 3.125

_button_key_map = {'s1' : 1, 's2' : 2, 's3' : 3, 's4' : 4}
_keypad_data = ""

class PageController():
    """ Manages the paging and event handling for the 40x2 display:
        on_tick called every 0.1 seconds as part of the main loop after the button read
        on_poll called every 1.5 seconds
        on_page called when a new page has been selected
        on_refresh called every 30 seconds"""
    def __init__(self,pixi_instance=None,on_page=None,on_poll=None,on_tick=None,on_refresh=None,ticks_poll=15,ticks_refresh=300):
        if pixi_instance is None:
            raise Exception('No pixi instance given')
        self.pixi = pixi_instance
        # Callbacks
        self.on_page = on_page
        self.on_poll = on_poll
        self.on_tick = on_tick
        self.on_refresh = on_refresh
        
        self.page = 1
        self.poll = ticks_poll
        self.poll_max = ticks_poll
        self.refresh = ticks_refresh
        self.refresh_max = ticks_refresh
        
        self._run = True
        
    def clear(self):
        self.pixi.display_clear()

    def run(self):
        if self.on_page != None:
            self.on_page()
        #main loop
        while self._run:
            key = None
            button_state = pixi.get_buttons()
            for button in button_state:
                if button_state[button]['now']:
                    key = _button_key_map[button]
                    self.pixi.set_off()
                    self.pixi.set_led('d%d'%key,'on')
                    self.pixi.update_leds()
                    break 

            if key is not None and key in [1,2,3,4] and self.page != key:
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
            time.sleep(0.05)
                    
    def threaded_run(self):
        self.threaded_runner = Thread(target=self.run)
        self.threaded_runner.start()

    def stop(self):
        print "Display stop called"
        self._run = False
        self.pixi.display_clear()



page_controller = None

def accelerometer_init():
    # save us writing the labels on every refresh
    pixi.display_clear()
    pixi.display_write("Accelerometer ", x=0, y=0)
    pixi.display_write("X", x=30, y=0)
    pixi.display_write("Y", x=9, y=1)
    pixi.display_write("Z", x=30, y=1)

def accelerometer():
    current_state = pixi.accel.get_value()

    if current_state['x'] > 32:
        pixi.display_bar_graph(x=21, y=0, length=9, percentage=int(perc_const * (32 - (current_state['x'] - 32))), reverse=True)
        pixi.display_bar_graph(x=31, y=0, length=9, percentage=0, reverse=False)
    else:
        pixi.display_bar_graph(x=21, y=0, length=9, percentage=0, reverse=True)
        pixi.display_bar_graph(x=31, y=0, length=9, percentage=int(perc_const * (current_state['x'])), reverse=False)

    if current_state['y'] > 32:
        pixi.display_bar_graph(x=0, y=1, length=9, percentage=int(perc_const * (32 - (current_state['y'] - 32))), reverse=True)
        pixi.display_bar_graph(x=10, y=1, length=9, percentage=0, reverse=False)
    else:
        pixi.display_bar_graph(x=0, y=1, length=9, percentage=0, reverse=True)
        pixi.display_bar_graph(x=10, y=1, length=9, percentage=int(perc_const * (current_state['y'])), reverse=False)

    if current_state['z'] > 32:
        pixi.display_bar_graph(x=21, y=1, length=9, percentage=int(perc_const * (32 - (current_state['z'] - 32))), reverse=True)
        pixi.display_bar_graph(x=31, y=1, length=9, percentage=0, reverse=False)
    else:
        pixi.display_bar_graph(x=21, y=1, length=9, percentage=0, reverse=True)
        pixi.display_bar_graph(x=31, y=1, length=9, percentage=int(perc_const * (current_state['z'])), reverse=False)

def analogue_init():
    # save us writing the labels on every refresh
    pixi.display_clear()
    pixi.display_write("Analogue Input", x=0, y=0)
    pixi.display_write("P", x=20, y=0)
    pixi.display_write("V", x=0, y=1)
    pixi.display_write("H", x=20, y=1)

def analogue():
    pixi.display_bar_graph(x=21, y=0, length=19, percentage=0.0244140625 * pixi.adc.read_input(0), reverse=False)
    pixi.display_bar_graph(x=1, y=1, length=19, percentage=0.0244140625 * pixi.adc.read_input(1), reverse=False)
    pixi.display_bar_graph(x=21, y=1, length=19, percentage=0.0244140625 * pixi.adc.read_input(2), reverse=False)

def magnatometer_init():
    # save us writing the labels on every refresh
    pixi.display_clear()
    pixi.display_write("Mag. ", x=0, y=0)
    pixi.display_write("X", x=5, y=0)
    pixi.display_write("Y", x=17, y=0)
    pixi.display_write("Z", x=29, y=0)
    pixi.display_write("Temp : ", x=0, y=1)
    
def magnatometer():
    global _keypad_data

    current_state = pixi.compass.get_value()
    
    pixi.display_write("%d" % current_state['x'], x=7, y=0)
    pixi.display_write("%d" % current_state['y'], x=19, y=0)
    pixi.display_write("%d" % current_state['z'], x=31, y=0)
    pixi.display_write("%d" % pixi.adc.read_input(2), x=8, y=1)
    
    """
    keypad_contents_list = pixi.keypad.read()
    for new_char in keypad_contents_list:
        _keypad_data = "%s%s" % (new_char,_keypad_data)

    # trim it to 10 chars
    _keypad_data = _keypad_data[:16]
    
    pixi.display_write(_keypad_data, x=9, y=1)    
    """
def get_addr(interface):
    try:
        s = subprocess.check_output(["ip","addr","show",interface])
        return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except:
        return '?.?.?.?'

def ip_and_datetime():
    dt=str(datetime.datetime.now())
    pixi.display_write(dt[:10], x=2, y=0)
    pixi.display_write(dt[11:19], x=3, y=1)
    pixi.display_write('eth0'+get_addr('eth0').rjust(15), x=18, y=0)
    #pixi.display_write('wlan0'+get_addr('wlan0').rjust(15), x=18, y=1)

# Callbacks
def on_page():
    page_controller.clear()
    if page_controller.page == 4:
        accelerometer_init()
        accelerometer()
    elif page_controller.page == 3:
        analogue_init()
        analogue()
    elif page_controller.page == 2:
        magnatometer_init()
        magnatometer()
    elif page_controller.page == 1:
        ip_and_datetime()

def on_poll():
    pass
    
def on_tick():
    if page_controller.page == 4:
        accelerometer()
    elif page_controller.page == 3:
        analogue()
    elif page_controller.page == 2:
        magnatometer()
    elif page_controller.page == 1:
        ip_and_datetime()

def on_refresh():
    pass
    """
    if page_controller.page == 1:
        accelerometer()
    elif page_controller.page == 2:
        analogue()
    elif page_controller.page == 3:
        magnatometer()
    elif page_controller.page == 4:
        ip_and_datetime()
    """
try:
    page_controller = PageController(pixi, on_page, on_poll, on_tick, on_refresh)
    page_controller.run()
except (KeyboardInterrupt, SystemExit):
    page_controller.stop()
    pixi.set_off()
    pixi.update_leds()

