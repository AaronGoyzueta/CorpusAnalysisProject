#!/usr/bin/env python

import json
import requests
import subprocess

BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'su9ikro99s1f8y25r0171b1iu36wbf'
TOKEN = 'Bearer a7yk1mbt2wt6lk17ml2q4ui61uyx73'

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": TOKEN
}

def main():
    with open("../TwitchChat/data/live-channels.json", "r") as source1:
        channel_json = json.load(source1)
        live_channels = channel_json["channels"]
    with open("../TwitchChat/data/channels-being-scraped.json", "r") as source2:
        channel_json = json.load(source2)
        being_scraped = channel_json["channels"]
    channels_being_scraped = set().union(*(d.keys() for d in being_scraped))
    print(f"currently scraping: {channels_being_scraped}")
    for channel in live_channels:
            channel_name, data = list(channel.items())[0]
            if channel_name not in channels_being_scraped:
                user_id = data[0]["id"]
                print(f"about to start scraping {channel_name}")
                subprocess.Popen(["python", "get-live-chat.py", channel_name, user_id])
                being_scraped.append(channel)
                channels_being_scraped.add(channel_name)
    live_channels = {}
    live_channels["channels"] = []
    new_being_scraped = {}
    new_being_scraped["channels"] = being_scraped
    with open("../TwitchChat/data/channels-being-scraped.json", "w") as sink1:
        json.dump(new_being_scraped, sink1, indent=4)
    with open("../TwitchChat/data/live-channels.json", "w") as sink2:
        json.dump(live_channels, sink2, indent=4)


if __name__ == "__main__":
    main()
