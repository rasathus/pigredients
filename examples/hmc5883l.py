from time import sleep
from pigredients.ics import hmc5883l as hmc5883l

# Using standard addresses so no need for any params.
compass = hmc5883l.HMC5883L(debug=False)

def write_direction():
    print "%s" % compass.get_value()
    #display.ser.write(str(direction).ljust(16))
    
while True:
    write_direction()
    sleep(0.25)          
        
