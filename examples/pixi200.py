from time import sleep
from pigredients.boards import pixi200 as pixi200

pixi = pixi200.PIXI200()
"""
for i in range(0,10):
    # check our buttons then sleep for a bit.
    pixi.get_buttons()
    sleep(2)
"""
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
