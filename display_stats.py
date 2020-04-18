#!/usr/bin/python3
# --------------------------------------
#             _          
#   __ _  ___| |__   ___ 
#  / _` |/ _ \ '_ \ / _ \
# | (_| |  __/ | | |  __/
#  \__,_|\___|_| |_|\___|
#                       
# Prints hardware stats like temperature, pressure, humidity, cpu, memory, disk, time, network on screen.
# The messages are optimized for 16x2 LCD display.
# -------------------------------------
import RPi.GPIO as GPIO
import time
import sys
import datetime
from drivers.lcd_16x2 import write_multiple_lines, gpio_init, write_diff

LCD_WIDTH = 16

def main():
    gpio_init()
    args = sys.argv
    if '-d' == args[1]:
        write_date_message(args[2] if len(args) > 2 else None)
    elif '-n' == args[1]:
        write_multiple_lines(get_network_message())
    elif '-t' == args[1]:
        write_multiple_lines(get_temperature_message())
    elif '-p' == args[1]:
        write_multiple_lines(get_pressure_message())
    elif '-h' == args[1]:
        write_multiple_lines(get_humidity_message())
    elif '-c' == args[1]:
        write_multiple_lines(get_cpu_message())
    elif '-m' == args[1]:
        write_multiple_lines(get_memory_message())
    elif '-l' == args[1]:
        write_multiple_lines(get_ambient_light_message())
    elif '-sn' == args[1]:
        scan_network()
    elif '-sw' == args[1]:
        update_weather_from_api()
    else:
        wrong_args_error()
        
def write_date_message(duration):
    if duration == None:
        write_multiple_lines(get_date_message())
    else:
        start = datetime.datetime.now()
        time_alive = int(duration)
        i = 0
        prev_message = None
        while (datetime.datetime.now() - start).total_seconds() < time_alive:
            if prev_message == None:
                prev_message = get_date_message()
                write_multiple_lines(prev_message)
            else:
                new_message = get_date_message()
                if prev_message == new_message:
                    time.sleep(0.25)
                else:
                    write_diff(prev_message, new_message, 0)
                    prev_message = new_message

def get_date_message():
    now = datetime.datetime.now()
    return (now.strftime('%a, %d %b %Y')).center(LCD_WIDTH) + now.strftime('%H:%M:%S').center(LCD_WIDTH)
    
def get_network_message():
    pass

def get_temperature_message():
    pass

def get_pressure_message():
    pass

def get_humidity_message():
    pass

def get_cpu_message():
    pass

def get_memory_message():
    pass

def get_ambient_light_message():
    pass

def scan_network():
    pass

def update_weather_from_api():
    pass

def wrong_args_error():
    print('''
    Invalid arguments passed. Use python3 display_stats.py argument
    Valid arguments are:
    ====================
    -d      : Displays date and time, arg2 decides time interval to refresh seconds
    -n      : Displays network stats
    -t      : Displays temperature from sensor and weather api
    -p      : Displays pressure from sensor and calculates sea level pressure
    -h      : Displays humidity from sensor and weather api
    -c      : Displays cpu usage and cpu temperature
    -m      : Displays memory and disk usage
    -l      : Displays ambient light, sunset / sunrise time
    -sn     : Scans the network using nmap
    -sw     : Calls weather api for current location
    ------------------------------------------------------------------------------
    Example :
    python3 display_stats.py -d 7
    python3 display_stats.py -n
    ''')
    raise Exception('Invalid arguments', str(sys.argv[1:]))
    
if __name__ == '__main__':
  main()
