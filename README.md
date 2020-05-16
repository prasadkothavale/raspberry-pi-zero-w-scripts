# Raspberry Pi Zero W Scripts
Scripts created for Raspberry Pi Zero W assistant using Google Assistant and Google Cloud SDK. Root folder `./` contains scrips written for features listed below, `./drivers` folder contains drivers written for external hardware connected through GPIO pins.

### Prerequisite
* Python3 with libraries: python3-gpiozero, redis, python-nmap, tcp-latency
* Google Assistant SDK
* Redis
* OMX Player or mpg123
* nmap

## Scripts
### Initial setup
Set scripts folder (this) in path environment variable `/home/pi/.profile`:
```sh
# set PI_HOME
export PI_HOME="/home/pi"

# set PATH to custom scripts folder if it exists
if [ -d "$PI_HOME/scripts" ] ; then
    export SCRIPTS="$PI_HOME/scripts"
    PATH="$PI_HOME/scripts:$PATH"
fi

# set PATH to custom drivers folder if it exists
if [ -d "$PI_HOME/scripts/drivers" ] ; then
    export DRIVERS="$SCRIPTS/drivers"
    PATH="$PI_HOME/scripts/drivers:$PATH"
fi
```

### hello_led_gpio.py
Sample program to turn on/off LEDs mounted on GPIO. 

### speak
Uses google cloud text to speech api to create mp3 speech files. Requires `omxplayer` (or `mpg123`) and `gcloud` cli (https://cloud.google.com/sdk/docs#deb)to be installed.
Refer https://cloud.google.com/text-to-speech/docs/quickstart-protocol for tutorial
Usage: `aehe-speak <setup|add|speak> [key] [text]`
```sh
# Setup speak (one time)
bash speak.sh install
# Create mp3 file from key and text
bash speak.sh add SAY_HELLO "Hello! This is Raspberry Pi Zero W"
# Play mp3 file for the key
bash speak.sh say SAY_HELLO
```

### internet_indicator.sh
This script pings `8.8.8.8` to check internet and sets GPIO(4) output 1 if internet connection is not available else will set it 0
Usage: `sudo bash internet_indecator.sh <start|check>`
##### Setup crontab to schedule the script
* Edit corntab config: `crontab -e`
* Configure start script on boot `@reboot sudo bash /home/pi/scripts/internet_indicator.sh start >/dev/null 2>&1`
* Configure check script every minute `* * * * * sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1`
Due to limitations of `crontab` above line schedules check per minute, to check every 20 seconds you can do
```
* * * * * sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
* * * * * sleep 20; sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
* * * * * sleep 40; sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
```

### display_stats.py
Prints hardware stats like temperature, pressure, humidity, cpu, memory, disk, time, network on screen. Usage `python3 display_stats.py argument`
Valid arguments are:
```
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
```
Example: 
```
python3 display_stats.py -d 7
python3 display_stats.py -n
```
##### Setup crontab to schedule the information to be displayed
* Edit corntab config: `crontab -e`
```
@reboot sudo /usr/bin/python3 /home/pi/scripts/drivers/lcd_16x2.py -i >/dev/null 2>&1
@reboot sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -sn >/dev/null 2>&1
@reboot sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -sw >/dev/null 2>&1
* * * * * sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -n >/dev/null 2>&1
* * * * * sleep 7.5; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -t >/dev/null 2>&1
* * * * * sleep 15; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -p >/dev/null 2>&1
* * * * * sleep 22.5; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -h >/dev/null 2>&1
* * * * * sleep 30; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -c >/dev/null 2>&1
* * * * * sleep 37.5; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -m >/dev/null 2>&1
* * * * * sleep 45; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -l >/dev/null 2>&1
* * * * * sleep 52.5; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -d 7 >/dev/null 2>&1
*/5 * * * * sleep 11; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -sn >/dev/null 2>&1
*/15 * * * * sleep 47; sudo /usr/bin/python3 /home/pi/scripts/display_stats.py -sw >/dev/null 2>&1
37 */4 * * * sleep 19; sudo /usr/bin/python3 /home/pi/scripts/drivers/lcd_16x2.py -i >/dev/null 2>&1
```

## Drivers
### bme280.py
_Assuming the python script is executed from root_`./`_folder_
```python
from drivers.bme280 import readBME280All
# returns tuple (temperature, pressure, humidity)
readBME280All()

```

### pwm_op.py
Creates pulse width modulation of `120Hz` with duty cycle of `0.6` on `GPIO 27`
Create service to start execution on startup
```sh
sudo nano /lib/systemd/system/pwm_op.service 
```
Add below contents
```
[Unit] 
Description=Create 120Hz 0.6 duty cycle pulse width modulation output 
After=multi-user.target 
 
[Service] 
Type=idle 
ExecStart=/usr/bin/python3 /home/pi/scripts/drivers/pwm_op.py 
 
[Install] 
WantedBy=multi-user.target 
```
Configure systemd
```sh
sudo systemctl daemon-reload 
sudo systemctl enable pwm_op.service 
```
