#!/usr/bin/env python

import json
import requests

BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'su9ikro99s1f8y25r0171b1iu36wbf'
TOKEN = 'Bearer a7yk1mbt2wt6lk17ml2q4ui61uyx73'

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": TOKEN
}


def is_live(channel):
    for channel_name, data in channel.items():
        user_id = data[0]["id"]
        query = f"streams?user_id={user_id}"
        url = BASE_URL + query
        response = requests.get(url, headers=HEADERS)
        data = response.json()["data"]
        if data:
            return True
        else:
            return False

def main():
    with open("../TwitchChat/data/not-live-channels.json") as source:
        channel_json = json.load(source)
        channels = channel_json["channels"]
    live_channels = []
    not_live_channels = []
    for channel in channels:
        if is_live(channel):
            live_channels.append(channel)
        else:
            not_live_channels.append(channel)
    live_json = {}
    live_json["channels"] = live_channels
    not_live_json = {}
    not_live_json["channels"] = not_live_channels
    with open("../TwitchChat/data/live-channels.json", "w") as sink1:
        json.dump(live_json, sink1, indent=4)
    with open("../TwitchChat/data/not-live-channels.json", "w") as sink2:
        json.dump(not_live_json, sink2, indent=4)


if __name__ == "__main__":
    main()
