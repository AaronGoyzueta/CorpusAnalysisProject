#!/usr/bin/env python

import argparse
import json
import re
import string

import pandas as pd

from pathlib import Path

#message_regex = re.compile('([0-9]{4}-[0-9]{2}-[0-9]{2})?_?([0-9]{2}:[0-9]{2}:[0-9]{2})?\s?-?\s?:(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*?) :(.*)')
date_regex = re.compile('[0-9]{4}-[0-9]{2}-[0-9]{2}')
time_regex = re.compile('[0-9]{2}:[0-9]{2}:[0-9]{2}')
chatter_regex = re.compile('@(.*).tmi')
channel_regex = re.compile('#(.*) :')
message_regex = re.compile('#.*? :(.*)$')
mpa = dict.fromkeys(range(32))

def parse_line(line, current_date, current_time):
    date = re.search(date_regex, line)
    if date:
        date = date.group()
    else:
        date = current_date
    time = re.search(time_regex, line)
    if time:
        time = time.group()
    else:
        time = current_time
    chatter = re.search(chatter_regex, line)
    if chatter:
        chatter = chatter.group(1)
    channel = re.search(channel_regex, line)
    if channel:
        channel = channel.group(1)
        message = re.search(message_regex, line)
        if message:
            message = message.group(1)
    else:
        message = re.search("\s-\s(.*)$", line)
        if message:
            message = message.group(1)
    return [date, time, chatter, channel, message], date, time

def clean_message(message):
    clean_message = message.translate(mpa)
    clean_message = re.sub(r"\\", "", clean_message)
    clean_message = re.sub("'", "", clean_message)
    clean_message = re.sub('"', "", clean_message)
    clean_message = re.sub("\.|,|!|\?|@|#|\[|\]|\{|\}|%|\^|&|\*|\$", "", clean_message)
    return clean_message

def check_for_emotes(message, emotes_json):
    found_emotes = set()
    for word in message.split():
        if word in emotes_json.keys():
            found_emotes.add((word, emotes_json[word]))
    if len(found_emotes) != 0:
        return found_emotes
    else:
        return None

def main(args):
    file_path = args.file_path
    file_name = re.search("chat/(.*).log", file_path).group(1)
    data = []
    with open("../TwitchChat/data/emotes/all_emotes.json", "r") as source:
        emotes_json = json.load(source)
    with open(file_path, "r") as source:
        line = source.readline().rstrip()
        current_date = "foo"
        current_time = "bar"
        while line:
            if "riceaaroni" not in line and "helix" not in line and "HTTPS" not in line and "PING :tmi" not in line:
                try:
                    line = line.encode("ascii", "ignore").decode("utf-8")
                    parsed_line, current_date, current_time = parse_line(line, current_date, current_time)
                    if len(parsed_line) != 5:
                        print(line)
                    parsed_line.append(clean_message(parsed_line[4]))
                    parsed_line.append(check_for_emotes(parsed_line[5], emotes_json))
                    parsed_line.append(file_name)
                    data.append(parsed_line)
                except Exception as e:
                    print(e)
                    print(line)
            line = source.readline().rstrip()
            if not line:
                i = 0
                while not line:
                    line = source.readline().rstrip()
                    i += 1
                    if i == 10:
                        break
    df = pd.DataFrame(data, columns = ["Date", "Time", "Chatter", "Channel", "Message", "Clean_Message", "Emotes", "Stream"])
    df_file = args.df_file
    if Path(df_file).is_file():
        df.to_csv(df_file, mode='a', header=False, sep="\t")
    else:
        df.to_csv(df_file, mode='w', header=True, sep="\t")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path")
    parser.add_argument("df_file")
    args = parser.parse_args()
    main(args)
