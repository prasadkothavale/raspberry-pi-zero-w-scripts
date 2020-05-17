#!bin/bash
# --------------------------------------
#             _          
#   __ _  ___| |__   ___ 
#  / _` |/ _ \ '_ \ / _ \
# | (_| |  __/ | | |  __/
#  \__,_|\___|_| |_|\___|
#                       
# Helper driver to turn on/off red, green, blue and white LEDs
# -------------------------------------
source /home/pi/.profile
red='16'
green='20'
blue='21'
white='26'

print_error() {
    echo -e '\e[91minvalid or incomplete arguments passed\e[39m'
    echo 'usage: led_gpio.sh <option> [red,green,blue,white [0,1]]'
    echo 'valid options are:'
    echo '---------------------------------------------------------------------'
    echo 'init  - initialize gpio'
    echo 'set   - set color on/off, required two arguments color and state(0,1)'
    echo '---------------------------------------------------------------------'
    echo 'example:'
    echo 'led_gpio.sh set red 1'
}

case $1 in
    init)
        for gpio in $red $green $blue $white; do
            echo $gpio > /sys/class/gpio/export || echo -e "\e[33mGPIO$gpio is already initialized\e[39m"
            echo 'out' > /sys/class/gpio/gpio$gpio/direction
        done
        
        # Just an indicator that script is started
        for i in {1..4}
        do
            for gpio in $red $green $blue $white; do
                echo "1" > /sys/class/gpio/gpio$gpio/value
                sleep 0.025
                echo "0" > /sys/class/gpio/gpio$gpio/value
                sleep 0.025
            done
        done
        ;;
        
    set)
        eval "gpio=\$$2" || print_error
        echo $3 > /sys/class/gpio/gpio$gpio/value || print_error
        ;;
    *)
        print_error
        ;;
esac
