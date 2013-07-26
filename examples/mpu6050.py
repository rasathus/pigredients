from time import sleep
from pigredients.ics import mpu6050 as mpu6050

# Using standard addresses so no need for any params.
accel_gyro = mpu6050.MPU6050(debug=False)

def get_accel():
    print "%s" % accel_gyro.get_accel()

while True:
    get_accel()
    sleep(0.25)          
        
