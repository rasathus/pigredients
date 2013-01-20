from time import sleep
from pigredients.boards import pixi200 as pixi200


pixi = pixi200.PIXI200(i2c_bus=1)

def get_switches():
	switch_state = pixi.get_buttons()
	pixi.set_off()
	# Switch 1
	if switch_state['s1']['now']:
		pixi.set_led('d1','on')
	else:
		pixi.set_led('d1','off')
	if switch_state['s1']['pressed']:
		pixi.set_led('d2','on')
	else:
		pixi.set_led('d2','off')
	# Switch 2
	if switch_state['s2']['now']:
		pixi.set_led('d3','on')
	else:
		pixi.set_led('d3','off')
	if switch_state['s2']['pressed']:
		pixi.set_led('d4','on')
	else:
		pixi.set_led('d4','off')
	# Switch 3
	if switch_state['s3']['now']:
		pixi.set_led('d5','on')
	else:
		pixi.set_led('d5','off')
	if switch_state['s3']['pressed']:
		pixi.set_led('d6','on')
	else:
		pixi.set_led('d6','off')
	# Switch 1
	if switch_state['s4']['now']:
		pixi.set_led('d7','on')
	else:
		pixi.set_led('d7','off')
	if switch_state['s4']['pressed']:
		pixi.set_led('d8','on')
	else:
		pixi.set_led('d8','off')

	pixi.update_leds()
	
try:
	while True:
		get_switches()
		sleep(0.05)
except (KeyboardInterrupt, SystemExit):
	pixi.set_off()
	pixi.update_leds()

