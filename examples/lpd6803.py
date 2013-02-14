import time
from random import randint

from pigredients.ics import lpd6803 as lpd6803

if __name__ == '__main__':

    led_chain = lpd6803.LPD6803_Chain(ics_in_chain=25)
    led_chain.all_off()
    led_chain.write()
    time.sleep(1)
    try:
        while True:
            led_chain.all_random()
            time.sleep(1)
            led_chain.set_white()
            led_chain.write()
            time.sleep(1)
            led_chain.set_red()
            led_chain.write()
            time.sleep(1)
            led_chain.set_green()
            led_chain.write()
            time.sleep(1)
            led_chain.set_blue()
            led_chain.write()
            time.sleep(1)
            led_chain.cycle()
            led_chain.write()
            time.sleep(1)


    except KeyboardInterrupt:
        led_chain.set_off()
        led_chain.write()
    