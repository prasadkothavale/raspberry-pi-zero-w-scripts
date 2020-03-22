# Raspberry Pi Zero W Scripts
Scripts created for Raspberry Pi Zero W assistant using Google Assistant and Google Cloud SDK

### hello_led_gpio.py
Sample program to turn on/off LEDs mounted on GPIO. 

### speak
Uses google cloud text to speech api to create mp3 speech files. Requires `omxplayer` (or mpg123) and `gcloud` cli (https://cloud.google.com/sdk/docs#deb)to be installed.
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
This script will set GPIO(4) output 1 if internet connection is not available else will set it 0
Usage: `sudo bash internet_indecator.sh <start|check>`
##### Setup crontab to schedule the script
* Edit corntab config: `conrntab -e`
* Configure start script on boot `@reboot sudo bash /home/pi/scripts/internet_indicator.sh start >/dev/null 2>&1`
* Configure check script every minute `* * * * * sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1`
Due to limitations of `crontab` above line schedules check per minute, to check every 20 seconds you can do
```
* * * * * sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
* * * * * sleep 20; sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
* * * * * sleep 40; sudo bash /home/pi/scripts/internet_indicator.sh check >/dev/null 2>&1
```
