#!bin/bash
#This script will be called on system startup

echo Initialize aehe startup routine 
source /home/pi/.profile

# initialize LCD screen
python3 $SCRIPTS/display_stats.py -e0
python3 $DRIVERS/lcd_16x2.py -i
python3 $DRIVERS/lcd_16x2.py -b1

# startup message
python3 $DRIVERS/lcd_16x2.py -l1 "  Raspberry Pi  "
python3 $DRIVERS/lcd_16x2.py -l2 "     Zero W     " 
bash speak.sh say ON_START_GREET
python3 $DRIVERS/lcd_16x2.py -b0
python3 $SCRIPTS/display_stats.py -e1

# End
echo -------------------------------------------------
echo Startup completed on `date` 
echo -------------------------------------------------
