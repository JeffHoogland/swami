#!/bin/bash
#Usage: ./changetime.sh <date> <hours> <minutes> <seconds>
echo "changetime.sh"
date -s "${1} ${2}:${3}:${4}"
