#!bin/bash
#This script will set GPIO(4) output 1 if internet connection is not available else will set it 0
case $1 in
    start)
        echo "4" > /sys/class/gpio/export
        echo "out" > /sys/class/gpio/gpio4/direction
        
        # Just an indicator that script is started
        for i in {1..4}
        do
            echo "1" > /sys/class/gpio/gpio4/value
            sleep 0.1
            echo "0" > /sys/class/gpio/gpio4/value
            sleep 0.1
        done
        ;;
    check)
        retry=3
        internet_flag=0
        while [ $retry -gt 0 ] && [ $internet_flag -eq 0 ]
        do
            ((retry=retry-1))
            internet_flag=`ping -q -w 1 -c 1 8.8.8.8 | grep -c "1 received"`
            if [ $internet_flag -eq 1 ] 
            then
                echo "0" > /sys/class/gpio/gpio4/value
            else
                echo "1" > /sys/class/gpio/gpio4/value
            fi
        done
        ;;
    *)
        echo 'error: require atleast one argument'
        echo 'internet_indecator.sh <start|check>'
        ;;
esac
