#!/bin/bash
#Usage: ./changetz.sh <new tz>
echo "changetz.sh"
cp -f /usr/share/zoneinfo/$1 /etc/localtime
