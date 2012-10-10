import time

from pigredients.ics import ic74hc595 as ic74hc595

HIGH = ic74hc595.HIGH
LOW = ic74hc595.LOW

number_of_registers = 2

if __name__ == '__main__':

    my_register = ic74hc595.Shift_Register(registers_in_chain=number_of_registers)
    my_register.all_off()
    my_register.write()
    
    my_register.set_pin(pin_id=0, register_id=0, state=HIGH)
    my_register.write()
    time.sleep(0.5)
    my_register.set_pin(pin_id=0, register_id=0, state=LOW)
    my_register.set_pin(pin_id=1, register_id=0, state=HIGH)
    my_register.write()
    time.sleep(0.5)
    my_register.set_pin(pin_id=1, register_id=0, state=LOW)
    my_register.set_pin(pin_id=2, register_id=0, state=HIGH)
    my_register.write()
    time.sleep(0.5)
    my_register.set_pin(pin_id=2, register_id=0, state=LOW)
    my_register.set_pin(pin_id=3, register_id=0, state=HIGH)
    my_register.set_pin(pin_id=4, register_id=0, state=HIGH)
    my_register.set_pin(pin_id=5, register_id=0, state=HIGH)
    my_register.set_pin(pin_id=6, register_id=0, state=HIGH)
    my_register.write()
    time.sleep(0.5)
    
    my_register.all_off()
    my_register.write()
    time.sleep(2.5)
    
    
    my_register.binary_count()
    

