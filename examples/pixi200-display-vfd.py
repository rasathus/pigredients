from time import sleep
from random import randint

from pigredients.boards import pixi200 as pixi200


pixi = pixi200.PIXI200(display_mode='vfd', display_width=40, display_height=2, debug=False)

try:
	"""
	x_cord=0
	y_cord=0
	while True:
		pixi.display_clear()
		pixi.display_write("PiXi-200",x=x_cord, y=y_cord )
		sleep(0.25)
		x_cord = randint(0,39)
		y_cord = randint(0,1)
		print "x : %d y : %d" % (x_cord, y_cord)
	"""
	# write out our axis labels.
	pixi.display_write("X", x=9, y=0)
	pixi.display_write("Y", x=30, y=0)
	pixi.display_write("Z", x=9, y=1)
	perc_const = (100 / 32.0)

	while True:
		current_state = pixi.accel.get_value()
		#pixi.display_clear()

		if current_state['x'] > 32:
			pixi.display_bar_graph(x=0, y=0, length=9, percentage=int(perc_const * (32 - (current_state['x'] - 32))), reverse=True)
			pixi.display_bar_graph(x=10, y=0, length=9, percentage=0, reverse=False)
		else:
			pixi.display_bar_graph(x=0, y=0, length=9, percentage=0, reverse=True)
			pixi.display_bar_graph(x=10, y=0, length=9, percentage=int(perc_const * (current_state['x'])), reverse=False)

		if current_state['y'] > 32:
			pixi.display_bar_graph(x=21, y=0, length=9, percentage=int(perc_const * (32 - (current_state['y'] - 32))), reverse=True)
			pixi.display_bar_graph(x=31, y=0, length=9, percentage=0, reverse=False)
		else:
			pixi.display_bar_graph(x=21, y=0, length=9, percentage=0, reverse=True)
			pixi.display_bar_graph(x=31, y=0, length=9, percentage=int(perc_const * (current_state['y'])), reverse=False)

		if current_state['z'] > 32:
			pixi.display_bar_graph(x=0, y=1, length=9, percentage=int(perc_const * (32 - (current_state['z'] - 32))), reverse=True)
			pixi.display_bar_graph(x=10, y=1, length=9, percentage=0, reverse=False)
		else:
			pixi.display_bar_graph(x=0, y=1, length=9, percentage=0, reverse=True)
			pixi.display_bar_graph(x=10, y=1, length=9, percentage=int(perc_const * (current_state['z'])), reverse=False)

		sleep(0.1)
	
except (KeyboardInterrupt, SystemExit):
	pixi.display_clear()

