from time import sleep
from pigredients.ics import mma7660 as mma7660

accel = mma7660.MMA7660(i2c_bus=1, debug=False)

def write_accel():
    print "Result : %s" % accel.get_value()
    #print "Sleep Count %s" % accel.get_sleepcount()
  
while True:
    #accel.get_face()
    write_accel()
    sleep(1)
