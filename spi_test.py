import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import time
import sys
import math

CHANNELS = [MCP.P0, MCP.P1]

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.CE0)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
#chan = AnalogIn(mcp, MCP.P0)
#print('Raw ADC Value: ', chan.value)
#print('ADC Voltage: ' + str(chan.voltage) + 'V')

#print('-----------------------------------------')

#chan = AnalogIn(mcp, MCP.P1)
#print('Raw ADC Value: ', chan.value)
#print('ADC Voltage: ' + str(chan.voltage) + 'V')
#print('-----------------------------------------')

header = '|   |'
for channel in CHANNELS:
    header += '  CH' + str(channel) + '  |'
print(header)
print('-' * len(header))
    
while (True):
    l1 = '|Raw|'
    l2 = '| V |'
    l3 = '|Mod|'
    for channel in CHANNELS:
        chan = AnalogIn(mcp, channel)
        l1 += str(chan.value).rjust(7) + '|'
        l2 += str(round(chan.voltage, 5)).rjust(7) + '|'
        l3 += str(int(chan.value/256)).rjust(7) + '|'
    print (l1)
    print (l2)
    print (l3)
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[F")
    time.sleep(1)
    
