#!bin/bash
# --------------------------------------
#             _          
#   __ _  ___| |__   ___ 
#  / _` |/ _ \ '_ \ / _ \
# | (_| |  __/ | | |  __/
#  \__,_|\___|_| |_|\___|
#                       
# This script will produce pulse width modulation signals on GPIO(27)
# -------------------------------------

import RPi.GPIO as GPIO
import time

PWM_OP = 27         # GPIO output pin
FREQUENCY = 120     # Hz
DUTY_CYCLE = 0.6    # 0 < duty_cycle < 1

time_on = DUTY_CYCLE / FREQUENCY
time_off = (1 - DUTY_CYCLE) / FREQUENCY

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_OP, GPIO.OUT)  

while True:
    GPIO.output(PWM_OP, True)
    time.sleep(time_on)
    GPIO.output(PWM_OP, False)
    time.sleep(time_off)
