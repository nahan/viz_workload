#!/bin/bash
# ./get_temperature TEMP_FILE

TEMP_FILE=$1\

nvidia-smi --query-gpu=temperature.gpu --format=csv > $TEMP_FILE
sed -i 1d $TEMP_FILE
awk '{sum+=$1}END{printf "%.2f\n",sum/NR}' $TEMP_FILE