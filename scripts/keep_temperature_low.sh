#!/bin/bash
# ./keep_temperature_low BASE_TEMP TEMP_FILE

# echo "entering keep..."

BASE_TEMP=$1
TEMP_FILE=$2
TEMP=`source get_temperature.sh $TEMP_FILE`

while [ "$TEMP" \> "$BASE_TEMP" ]
do
    echo "The average temperature on GPUs is higher than the baseline, wait 10 seconds"
    sleep 10
    TEMP=`source get_temperature.sh $TEMP_FILE`
done

# echo $TEMP
# echo $BASE_TEMP

# echo "leaving keep..."