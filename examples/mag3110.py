from time import sleep
from pigredients.ics import mag3110 as mag3110

# Using standard addresses so no need for any params.
compass = mag3110.MAG3110(i2c_bus=1, debug=False)

def write_direction():
    print "Result : %s" % compass.get_value()
    #print "Heading : %s" % compass.get_heading()
    #display.ser.write(str(direction).ljust(16))
    
while True:
    write_direction()
    print "Die Temp : %d" % compass.get_temp() 
    sleep(0.5)          
        
