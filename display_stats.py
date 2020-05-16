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
import redis
import nmap
import os
import math
from tcp_latency import measure_latency
from drivers.lcd_16x2 import write_line, write_multiple_lines, gpio_init, write_diff
from drivers.bme280 import readBME280All

LCD_WIDTH = 16
INTERNET_INDICATOR_GPIO = 4
HEIGHT_ABOVE_SEA_LEVEL = 36         # meters
BAROMETRIC_CONSTANT = 0.00012 * -1  # https://www.math24.net/barometric-formula/

args = sys.argv
redis_cache = redis.Redis(host='localhost', port=6379, db=0)
display_stats_enabled = redis_cache.get('display_stats_enabled')

def main():
    gpio_init()
    
    if '-d' == args[1]:
        write_date_message(args[2] if len(args) > 2 else None)
        
    elif '-e0' == args[1]:
        redis_cache.set('display_stats_enabled', str(False))
        
    elif '-e1' == args[1]:
        redis_cache.set('display_stats_enabled', str(True))
        
    elif '-n' == args[1]:
        write_network_message()
        
    elif '-t' == args[1]:
        write_multiple_lines(get_temperature_message())
        
    elif '-p' == args[1]:
        write_multiple_lines(get_pressure_message())
        
    elif '-h' == args[1]:
        write_multiple_lines(get_humidity_message())
        
    elif '-c' == args[1]:
        #write_multiple_lines(get_cpu_message())
        write_date_message(args[2] if len(args) > 2 else None)
        
    elif '-m' == args[1]:
        #write_multiple_lines(get_memory_message())
        write_network_message()
        
    elif '-l' == args[1]:
        #write_multiple_lines(get_ambient_light_message())
        write_multiple_lines(get_temperature_message())
        
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
    
def write_network_message():
    write_multiple_lines(
        redis_cache.get('ip_address').decode().ljust(LCD_WIDTH) + 
        'Hosts:' + redis_cache.get('network_hosts').decode().rjust(LCD_WIDTH - 6)
    )
    
    time.sleep(1)
    
    write_multiple_lines(
        'Gateway:' + redis_cache.get('gateway_latency').decode().rjust(LCD_WIDTH - 8) +
        'Google:' + redis_cache.get('google_latency').decode().rjust(LCD_WIDTH - 7)
    )
    
def get_temperature_message():
    return 'Indoor:' + str(round(readBME280All()[0], 1)).rjust(LCD_WIDTH - 9) + chr(0xdf) + 'C' +\
        'Outdoor:' + redis_cache.get('outdoor_temperature').decode().rjust(LCD_WIDTH - 8)

def get_pressure_message():
    pressure = readBME280All()[1]
    sea_level_pressure = round(pressure / math.exp(BAROMETRIC_CONSTANT * HEIGHT_ABOVE_SEA_LEVEL), 1)
    return 'Air hPA:' + str(round(pressure, 1)).rjust(LCD_WIDTH - 8) + 'Sea hPA:' + str(sea_level_pressure).rjust(LCD_WIDTH - 8)

def get_humidity_message():
    return 'Humid. I:' + str(round(readBME280All()[2], 1)).rjust(LCD_WIDTH - 10) + '%' +\
        'Humid. O:' + redis_cache.get('outdoor_humidity').decode().rjust(LCD_WIDTH - 9)

def get_cpu_message():
    pass

def get_memory_message():
    pass

def get_ambient_light_message():
    pass

def scan_network(retry=3):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(INTERNET_INDICATOR_GPIO, GPIO.OUT)
    redis_cache.set('network_hosts', '...')
    redis_cache.set('gateway_latency', '...')
    redis_cache.set('google_latency', '...')
    redis_cache.set('ip_address', 'IP Unavailable')
        
    if GPIO.input(INTERNET_INDICATOR_GPIO) == 0:
        redis_cache.set('ip_address', os.popen("ifconfig wlan0 | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*'").read().strip())
        gateway_ip = os.popen("route -n | grep 'UG[ \t]' | awk '{print $2}'").read().strip()
        nm = nmap.PortScanner()
        redis_cache.set('network_hosts', nm.scan(hosts=gateway_ip[:-1]+'0/24',arguments='-sP')['nmap']['scanstats']['uphosts'])
        redis_cache.set('gateway_latency', '{:.0f}ms'.format(sum(measure_latency(host=gateway_ip, runs=10))/10))
        redis_cache.set('google_latency', '{:.0f}ms'.format(sum(measure_latency('www.google.com', runs=10))/10))
    elif retry > 0:
        time.sleep(10)
        scan_network(retry - 1)

def update_weather_from_api():
    redis_cache.set('outdoor_temperature', '...')
    redis_cache.set('outdoor_humidity', '...')

def wrong_args_error():
    print('''
    Invalid arguments passed. Use python3 display_stats.py argument
    Valid arguments are:
    ====================
    -d      : Displays date and time, arg2 decides time interval to refresh seconds
    -e0     : Disables display stats
    -e1     : Enables display stats
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
    
if __name__ == '__main__' and ((
    display_stats_enabled is not None and display_stats_enabled.decode() == 'True') or 
    args[1] in ['-sn', '-sw', '-e1', '-e0']
):
    main()
