from gpiozero import LED
from time import sleep

print('Running LED 17')
leds = [LED(2),LED(3),LED(4),LED(17),LED(27)]
#led = LED(17)

while True:
	for led in leds:
		led.on()
		sleep(0.07)
		led.off()

#	led.on()
#	sleep(0.25)
#	led.off()
#	sleep(0.25)

