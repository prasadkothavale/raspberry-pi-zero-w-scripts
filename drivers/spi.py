#!/usr/bin/python3
# --------------------------------------
#             _          
#   __ _  ___| |__   ___ 
#  / _` |/ _ \ '_ \ / _ \
# | (_| |  __/ | | |  __/
#  \__,_|\___|_| |_|\___|
#                       
# This is driver for SPI listening on CE0 for configured CHANNELS on MCP3008
# -------------------------------------

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import sys
import math
import os
from datetime import datetime
from lcd_16x2 import gpio_init, lcd_init, write_multiple_lines, set_backlight, get_backlight
import redis

# Channels to listen
MODE_SELECT     = MCP.P0
TEMT6000        = MCP.P1
CHANNELS        = [MODE_SELECT, TEMT6000]
REFRESH_TIME    = 0.5   # seconds

MAX_RESOLUTION      = 65536 
MODE_SELECT_FACTOR  = 8192
TEMT6000_FACTOR     = 256

WAIT_TO_APPLY_MODE  = 1     # seconds (int)

MODE_NEUTRAL        = 0
MODE_RESET_SCREEN   = 1
MODE_TOGGLE_MUTE    = 2
MODE_TOGGLE_BKLGHT  = 3

# initialize
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.CE0)
mcp = MCP.MCP3008(spi, cs)
gpio_init()
redis_cache = redis.Redis(host='localhost', port=6379, db=0)

analog_channels = []
for channel in CHANNELS:
    analog_channels.append(AnalogIn(mcp, channel))
    
last_selected_mode = 0
last_selected_mode_set = datetime.now()
mode_action_pending = False;
last_backlight_status = get_backlight()

"""Channel routing function"""    
def channel_listener(channel, value, voltage):
    if channel == MODE_SELECT:
        handle_mode_select(channel, value, voltage)
    elif channel == TEMT6000:
        handle_temt6000(channel, value, voltage)

"""process mode select channel values"""
def handle_mode_select(channel, value, voltage):
    global last_selected_mode
    global mode_action_pending
    global last_selected_mode_set
    global last_backlight_status
    reduced_value = int(value/MODE_SELECT_FACTOR)

    if not (last_selected_mode == reduced_value):
        last_selected_mode = reduced_value
        last_selected_mode_set = datetime.now()
        mode_action_pending = True
        os.popen("mpg123 -q /home/pi/.data/sounds/tick.mp3")
        redis_cache.set('display_stats_enabled', str(False))
        set_backlight(True)
        
        if MODE_NEUTRAL == reduced_value:
            write_multiple_lines("MODE:          0Neutral         ")
        elif MODE_RESET_SCREEN == reduced_value:
            write_multiple_lines("MODE:          1LCD Reset       ")
        else:
            write_multiple_lines("MODE:          " + str(reduced_value) + "Not Set         ")

    elif mode_action_pending and (datetime.now() - last_selected_mode_set).seconds > WAIT_TO_APPLY_MODE:
        mode_action_pending = False;
        for x in range(3):
            os.popen("bash /home/pi/scripts/drivers/led_gpio.sh set green 1")
            time.sleep(0.25)
            os.popen("bash /home/pi/scripts/drivers/led_gpio.sh set green 0")
            time.sleep(0.25)
        
        if MODE_NEUTRAL == reduced_value:
            pass
        elif MODE_RESET_SCREEN == reduced_value:
            lcd_init()
        else:
            for x in range(3):
                os.popen("bash /home/pi/scripts/drivers/led_gpio.sh set red 1")
                time.sleep(0.25)
                os.popen("bash /home/pi/scripts/drivers/led_gpio.sh set red 0")
                time.sleep(0.25)
                
        redis_cache.set('display_stats_enabled', str(True))
        set_backlight(last_backlight_status)
            

"""process temt6000 sensor input"""
def handle_temt6000(channel, value, voltage):
    reduced_value = int(value/TEMT6000_FACTOR)

# The main loop
while True:
    for channel in CHANNELS:
        chan = analog_channels[channel]
        channel_listener(channel, chan.value, chan.voltage)
    time.sleep(REFRESH_TIME)
