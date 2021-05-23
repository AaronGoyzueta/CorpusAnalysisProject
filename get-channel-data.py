import json
import requests

BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'su9ikro99s1f8y25r0171b1iu36wbf'
TOKEN = 'Bearer a7yk1mbt2wt6lk17ml2q4ui61uyx73'

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": TOKEN
}


def main():
    path = "../TwitchChat/data/streamers.txt"
    channels = []
    channel_data = []
    channel_ids = []
    with open(path, "r") as source:
        line = source.readline()
        while line:
            channels.append(line.strip())
            line = source.readline()
    for channel in channels:
        query = f"users?login={channel}"
        url = BASE_URL + query
        response = requests.get(url, headers=HEADERS)
        data = response.json()['data'][0]
        d = {}
        lst = []
        lst.append(data)
        d[channel] = lst
        channel_data.append(d)
    channel_json = {}
    channel_json["channels"] = channel_data
    with open("../TwitchChat/data/channels.json", "w") as sink1:
        json.dump(channel_json, sink1, indent=4)
    with open("../TwitchChat/data/not-live-channels.json", "w") as sink2:
        json.dump(channel_json, sink2, indent=4)


if __name__ == "__main__":
    main()
