# Raspberry Pi Zero W Scripts
Scripts created for Raspberry Pi Zero W assistant using Google Assistant and Google Cloud SDK

### hello_led_gpio.py
Sample program to turn on/off LEDs mounted on GPIO. 

### speak
Uses google cloud text to speech api to create mp3 speech files. Requires `omxplayer` and `gcloud` cli (https://cloud.google.com/sdk/docs#deb)to be installed.
Refer https://cloud.google.com/text-to-speech/docs/quickstart-protocol for tutorial
Usage: `aehe-speak <setup|add|speak> [key] [text]`
```sh
# Setup speak (one time)
bash speak.sh install
# Create mp3 file from key and text
bash speak.sh add SAY_HELLO "Hello! This is Raspberry Pi Zero W"
# Play mp3 file for the key
bash speak.sh speak SAY_HELLO
```
