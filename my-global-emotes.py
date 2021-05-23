import json

d = {}
d["global emotes"] = []
with open("../TwitchChat/data/global.txt", "r") as source:
    __ = source.readline()
    line = source.readline().rstrip()
    while line:
        d["global emotes"].append(line)
        __ = source.readline()
        line = source.readline().rstrip()
with open("../TwitchChat/data/jsons/global_emotes.json", "r") as source:
    data = json.load(source)
    current_emotes = data["global emotes"]
    d["global emotes"] = d["global emotes"] + current_emotes
    with open("../TwitchChat/data/jsons/global_emotes.json", "w") as sink:
        json.dump(d, sink, indent=4)