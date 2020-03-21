#!bin/bash
#This script will be called on system startup

echo Initialize aehe startup routine 
source /home/pi/.profile

bash speak.sh say ON_START_GREET

# End
echo -------------------------------------------------
echo Startup completed on `date` 
echo -------------------------------------------------
