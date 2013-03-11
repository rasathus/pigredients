import time

from pigredients.ics import lpd8806 as lpd8806

if __name__ == '__main__':

    led_chain = lpd8806.LPD8806_Chain()
    led_chain.all_off()
    led_chain.write()
    
    led_chain.set_ic(ic_id=24, rgb_value=[255,0,255])
    led_chain.write()
    time.sleep(2)
    led_chain.set_ic(ic_id=24, rgb_value=[0,0,0])
    led_chain.write()
    time.sleep(0.5)
    
    led_chain.set_white()
    led_chain.write()
    time.sleep(0.5)
    led_chain.set_red()
    led_chain.write()
    time.sleep(0.5)
    led_chain.set_green()
    led_chain.write()
    time.sleep(0.5)
    led_chain.set_blue()
    led_chain.write()
    time.sleep(0.5)
    led_chain.set_white()
    led_chain.write()
    time.sleep(0.5)    
    led_chain.cycle()    
    
    led_chain.set_off()
    led_chain.write()
    
    
