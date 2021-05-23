#!/bin/bash

trap "kill $(jobs -p); ./reset-jsons.py" EXIT

python reset-jsons.py
python get-channel-data.py

while :
do
    ./check-if-live.py
    ./start-scraping-channels.py
    sleep 300
done

