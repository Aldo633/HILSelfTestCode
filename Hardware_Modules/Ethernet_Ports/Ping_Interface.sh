#!/bin/bash                                                            
#Ping_Interface.sh

if [ $# -eq 3 ]; then
    Source="$1"
    Destination="$2"
    Count_Replies="$3"
elif [ $# -eq 2 ]; then
    Source="$1"
    Destination="$2"
    Count_Replies=2
else
    echo "Usage: $0 <source> <destination> [count_replies]"
    exit 1
fi

ping -c "$Count_Replies" -I "$Source" "$Destination"

#ping -c 4 -I 192.168.2.82 192.168.2.34


