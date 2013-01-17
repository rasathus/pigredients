from time import sleep
from pigredients.boards import pixi200 as pixi200


pixi = pixi200.PIXI200(i2c_bus=1)

"""
for i in range(0,10):
    # check our buttons then sleep for a bit.
    pixi.get_buttons()
    sleep(2)
"""
"""
# Some examples of led set and unset.
pixi.set_led('d1','on')
pixi.set_led('d2','slow')
pixi.set_led('d3','fast')
pixi.set_led('d4','off')
pixi.set_led('d5','on')
pixi.set_led('d6','slow')
pixi.set_led('d7','fast')
pixi.set_led('d8','off')
pixi.update_leds()
sleep(2)
pixi.set_led('d1','off')
pixi.set_led('d2','on')
pixi.set_led('d3','slow')
pixi.set_led('d4','fast')
pixi.set_led('d5','off')
pixi.set_led('d6','on')
pixi.set_led('d7','slow')
pixi.set_led('d8','fast')
pixi.update_leds()
sleep(2)
pixi.set_led('d1','off')
pixi.set_led('d2','off')
pixi.set_led('d3','off')
pixi.set_led('d4','off')
pixi.set_led('d5','off')
pixi.set_led('d6','off')
pixi.set_led('d7','off')
pixi.set_led('d8','off')
pixi.update_leds()
"""

# a fun little spirit level using the leds to visualise the accelerometer data.
def vis_accel():
	current_state = pixi.accel.get_value()
	#print "Current Accel Vals : %s" % current_state
	if current_state['y'] > 39 and current_state['y'] <= 45:
		pixi.set_off()
		pixi.set_led('d1','on')
		pixi.set_led('d2','on')
		pixi.update_leds()

	elif current_state['y'] > 45 and current_state['y'] <= 53:
		pixi.set_off()
		pixi.set_led('d2','on')
		pixi.set_led('d3','on')
		pixi.update_leds()

	elif current_state['y'] > 53 and current_state['y'] <= 60:
		pixi.set_off()
		pixi.set_led('d3','on')
		pixi.set_led('d4','on')
		pixi.update_leds()

	elif current_state['y'] > 60 or current_state['y'] < 5:
		pixi.set_off()
		pixi.set_led('d4','on')
		pixi.set_led('d5','on')
		pixi.update_leds()

	elif current_state['y'] > 5 and current_state['y'] <= 12:
		pixi.set_off()
		pixi.set_led('d5','on')
		pixi.set_led('d6','on')
		pixi.update_leds()

	elif current_state['y'] > 12 and current_state['y'] <= 17:
		pixi.set_off()
		pixi.set_led('d6','on')
		pixi.set_led('d7','on')
		pixi.update_leds()

	elif current_state['y'] > 17 and current_state['y'] <= 25:
		pixi.set_off()
		pixi.set_led('d7','on')
		pixi.set_led('d8','on')
		pixi.update_leds()

	else:
		pixi.set_off()
		pixi.update_leds()

try:
	while True:
		vis_accel()
		#sleep(0.25)
except (KeyboardInterrupt, SystemExit):
	pixi.set_off()
	pixi.update_leds()

