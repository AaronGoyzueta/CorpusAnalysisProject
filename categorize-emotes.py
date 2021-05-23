#!/usr/bin/env python

import json
import os

def get_emotes_from_json(file_path, all_emotes):
    with open(file_path, "r") as source:
        emote_json = json.load(source)
        if emote_json == {"error":"Channel not found"}:
            pass
        else:
            channel = emote_json['channel_name']
            emotes = emote_json["emotes"]
            for emote in emotes:
                emote_name = emote["code"]
                all_emotes[emote_name] = channel


def main():
    emote_folder = "../TwitchChat/data/emotes/"
    all_emotes = {}
    for file in os.listdir(emote_folder):
        if file.endswith(".json") and file != "all_emotes.json":
            get_emotes_from_json(emote_folder + file, all_emotes)
    with open(emote_folder + "ffz_emotes.txt", "r") as source:
        line = source.readline().rstrip()
        while line:
            all_emotes[line] = "FFZ"
            line = source.readline().rstrip()
    emote_type = "GLOBAL"
    with open(emote_folder + "global_emotes.txt", "r") as source:
        line = source.readline().rstrip()
        if line == "BTTV EMOTES":
            emote_type = "BTTV"
        while line:
            if line == "BTTV EMOTES":
                emote_type = "BTTV"
            else:
                all_emotes[line] = emote_type
            line = source.readline().rstrip()
    with open(emote_folder + "all_emotes.json", "w") as sink:
        json.dump(all_emotes, sink, indent=4)


if __name__ == '__main__':
    main()
