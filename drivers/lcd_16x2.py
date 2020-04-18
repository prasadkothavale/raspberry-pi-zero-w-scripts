#!/usr/bin/python3
# --------------------------------------
#             _          
#   __ _  ___| |__   ___ 
#  / _` |/ _ \ '_ \ / _ \
# | (_| |  __/ | | |  __/
#  \__,_|\___|_| |_|\___|
#                       
# The original script is modified to convert example into driver
# Backlight is connected to GPIO pin to control backlight on/off.
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#  lcd_16x2.py
#  16x2 LCD Test Script
#
# Author : Matt Hawkins
# Date   : 06/04/2015
#
# http://www.raspberrypi-spy.co.uk/
#
# Copyright 2015 Matt Hawkins
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V                     - Some displays run on 5V
# 3 : Contrast (0-5V)*       - 0V (Ground) 
# 4 : RS (Register Select)   - GPIO 7
# 5 : R/W (Read Write)       - Ground
# 6 : Enable or Strobe       - GPIO 8
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4             - GPIO 25
# 12: Data Bit 5             - GPIO 24
# 13: Data Bit 6             - GPIO 23
# 14: Data Bit 7             - GPIO 18
# 15: LCD Backlight          - GPIO 17
# 16: LCD Backlight GND      - Ground

#import
import RPi.GPIO as GPIO
import time
import sys

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
LCD_D7 = 18
LCD_BK = 17


# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

SCROLL_SPEED = 4 # Characters/Second (Never set it 0)

""" Main program to run driver script from command line """
def main():
  args = sys.argv
  if '-b0' == args[1]:
    set_backlight(False)
  elif '-b1' == args[1]:
    set_backlight(True)
  elif '-c' == args[1]:
    clear()
  elif '-ch' == args[1] and not (None == args[2] and None == args[3]) and ',' in args[3]:
    write_character(args[2][0], list(map(int, args[3].split(','))))
  elif '-i' == args[1]:
    lcd_init()
  elif '-l1' == args[1] and not (None == args[2]):
    write_line(args[2], True)
  elif '-l2' == args[1] and not (None == args[2]):
    write_line(args[2], False)
  elif '-m' == args[1] and not (None == args[2]):
    write_multiple_lines(args[2])
  else:
    print_wrong_args_error()
  
""" Writes single line specified, scrolls if more than LCD_WIDTH characters """
def write_line(text, is_first, initial_delay = 1.5):
    lcd_line = LCD_LINE_1 if is_first else LCD_LINE_2
    text = text.ljust(LCD_WIDTH, ' ')
    text_length = len(text)
    text_pointer = 0
    
    lcd_string(text[text_pointer : text_pointer + LCD_WIDTH], lcd_line)
    time.sleep(initial_delay)
    while text_pointer < text_length - LCD_WIDTH:
        text_pointer += 1
        lcd_string(text[text_pointer : text_pointer + LCD_WIDTH], lcd_line)
        time.sleep(1/SCROLL_SPEED)

""" Writes provided text on line 1, overflow text is carried over line 2.
Scrolls if text length is more that 2 x LCD_WIDTH """
def write_multiple_lines(text, initial_delay = 2):
    text = text.ljust(2 * LCD_WIDTH)
    text_length = len(text)
    text_pointer = 0
    
    lcd_string(text[text_pointer : text_pointer + LCD_WIDTH], LCD_LINE_1)
    lcd_string(text[text_pointer + LCD_WIDTH : text_pointer + 2*LCD_WIDTH], LCD_LINE_2)
    time.sleep(initial_delay)
    while text_pointer < text_length - 2*LCD_WIDTH:
        text_pointer += 1
        lcd_string(text[text_pointer : text_pointer + LCD_WIDTH], LCD_LINE_1)
        lcd_string(text[text_pointer + LCD_WIDTH : text_pointer + 2*LCD_WIDTH], LCD_LINE_2)
        time.sleep(1/SCROLL_SPEED)

""" Writes provided character to a specific screen location [x,y] """
def write_character(character, location):
    if (character == None or character == ''):
        character = ' '
    character_byte = ord(character[0])
    memory_addr = (LCD_LINE_1 if location[1] == 0 else LCD_LINE_2) + location[0]
    lcd_byte(memory_addr, LCD_CMD)
    lcd_byte(ord(character[0]), LCD_CHR)
    
""" Only writes the difference between old_text and new_text, 
    supported modes are:
    0: Both lines
    1: Line 1 only
    2: Line 2 only """
def write_diff(old_text, new_text, mode):
    if 0 == mode:
        old_text = old_text.ljust(2 * LCD_WIDTH)[-2 * LCD_WIDTH : ]
        new_text = new_text.ljust(2 * LCD_WIDTH)[-2 * LCD_WIDTH : ]
    else:
        old_text = old_text.ljust(LCD_WIDTH)[-1 * LCD_WIDTH : ]
        new_text = new_text.ljust(LCD_WIDTH)[-1 * LCD_WIDTH : ]

    index = 0
    while index < len(old_text):
        if not old_text[index] == new_text[index]:
            x = index % LCD_WIDTH
            y = int(index/LCD_WIDTH) if mode == 0 else mode - 1
            write_character(new_text[index], [x, y])
        index += 1

""" Clears screen """
def clear():
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display

""" Set backlight on/off """
def set_backlight(status):
    GPIO.output(LCD_BK, status)
    
""" GPIO cleanup """
def gpio_cleanup():
    GPIO.cleanup()

""" Initialise GPIO output """
def gpio_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
    GPIO.setup(LCD_E, GPIO.OUT)  # E
    GPIO.setup(LCD_RS, GPIO.OUT) # RS
    GPIO.setup(LCD_D4, GPIO.OUT) # DB4
    GPIO.setup(LCD_D5, GPIO.OUT) # DB5
    GPIO.setup(LCD_D6, GPIO.OUT) # DB6
    GPIO.setup(LCD_D7, GPIO.OUT) # DB7
    GPIO.setup(LCD_BK, GPIO.OUT) # BK

""" Initialise display """
def lcd_init():
    lcd_byte(0x33,LCD_CMD) # 110011 Initialise
    lcd_byte(0x32,LCD_CMD) # 110010 Initialise
    lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
    lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
    lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
    lcd_byte(0x01,LCD_CMD) # 000001 Clear display
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH,' ')

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
    
def print_wrong_args_error():
  print('''
  Invalid arguments passed, usage: python3 lcd_16x2.py arg1 [arg2]
  valid arguments are:
  ====================
  -b0   : Turns backlight off
  -b1   : Turns backlight on
  -c    : Clears the screen
  -ch   : Writes character at provided location x,y
  -i    : Sets GPIO outputs and initializes the display
  -l1   : Writes provided string in arg2 on line 1
  -l2   : Writes provided string in arg2 on line 2
  -m    : Writes provided string in arg2 on both the lines
  -----------------------------------------------------------------
  Example:
  python3 lcd_16x2.py -i
  python3 lcd_16x2.py -c
  python3 lcd_16x2.py -l1 "This is line 1"
  python3 lcd_16x2.py -ch A 6,0
  ''');

if __name__ == '__main__':
  gpio_init()
  main()
