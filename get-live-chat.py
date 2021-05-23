#!/usr/bin/env python

import argparse
import logging
import re
import requests
import socket
import time
import json

from datetime import datetime
from dateutil.tz import tzlocal
from emoji import demojize
from pathlib import Path


BASE_URL = 'https://api.twitch.tv/helix/'
CLIENT_ID = 'su9ikro99s1f8y25r0171b1iu36wbf'
TOKEN = 'Bearer a7yk1mbt2wt6lk17ml2q4ui61uyx73'

HEADERS = {
    "Client-ID": CLIENT_ID,
    "Authorization": TOKEN
}


def restore_channel(channel_name):
    with open("../TwitchChat/data/not-live-channels.json", "r") as source:
        channel_json = json.load(source)
        channels = channel_json["channels"]
        channel_names = set().union(*(d.keys() for d in channels))
    if channel_name not in channel_names:
        query = f"users?login={channel_name}"
        url = BASE_URL + query
        response = requests.get(url, headers=HEADERS)
        data = response.json()['data'][0]
        channel = {}
        lst = []
        lst.append(data)
        channel[channel_name] = lst
        channels.append(channel)
        channel_json = {}
        channel_json["channels"] = channels
        with open("../TwitchChat/data/not-live-channels.json", "w") as sink:
            json.dump(channel_json, sink, indent=4)

def remove_channel_from_being_scraped(channel_name):
    with open("../TwitchChat/data/channels-being-scraped.json", "r") as source:
        channel_json = json.load(source)
        channels = channel_json["channels"]
    for channel in channels:
        for name, data in channel.items():
            if name == channel_name:
                channels.remove(channel)
    channel_json = {}
    channel_json["channels"] = channels
    with open("../TwitchChat/data/channels-being-scraped.json", "w") as sink:
        json.dump(channel_json, sink, indent=4)

def is_still_live(user_id):
    query = f"streams?user_id={user_id}"
    url = BASE_URL + query
    response = requests.get(url, headers=HEADERS)
    if response.json()["data"]:
        return True
    else:
        return False

def main(args):
    channel = '#' + args.channel_name
    server = 'irc.chat.twitch.tv'
    port = 6667
    nickname = 'RiceAaroni'
    token = 'oauth:hfjlm0jak9cic6nbbiodf1js3wetsa'
    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\n".encode('utf-8'))
    try:
        resp = sock.recv(2048).decode('utf-8')
    except ConnectionResetError:
        with open("mistakes.txt", "a") as sink:
            print("ConnectionResetError: ")
            print(sock.recv(2048), file=sink)
    start = time.perf_counter()
    while True:
        now = time.perf_counter()
        if now > start + (60*5):
            start = now
            if is_still_live(args.user_id) == False:
                break
        try:
            resp = sock.recv(2048).decode('utf-8')
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
            elif len(resp) > 0:
                logging.info(demojize(resp))
        except:
            with open("mistakes.txt", "a") as sink:
                print(sock.recv(2048), file=sink)
    print(f"{args.channel_name} is no longer live")
    restore_channel(args.channel_name)
    remove_channel_from_being_scraped(args.channel_name)

    # regex = re.compile(':?(.*)\!.*@.*\.tmi\.twitch\.tv PRIVMSG #(.*) :(.*)')

    """
    with open(tsv_path, "w") as sink:
        print("TIME\tCHANNEL\tMESSAGE\tUSER", file=sink)
        while True:
            try:
                resp = sock.recv(2048).decode('utf-8')
                if resp.startswith('PING'):
                    sock.send("PONG\n".encode('utf-8'))
                elif nickname.casefold() in resp:
                    pass
                elif len(resp) > 0:
                    time = datetime.now(tzlocal()).strftime(
                        "%m/%d/%Y, %H:%M:%S %Z")
                    try:
                        matches = re.findall(regex, resp)
                        for match in matches:
                            username, stream, message = match
                            print(
                                f"{time}\t{stream}\t{message.rstrip()}\t{username.rstrip()}", file=sink)
                    except:
                        with open("mistakes.txt", "a") as sink:
                            print(resp, file=sink)
            except:
                with open("mistakes.txt", "a") as sink:
                    print("encoding error", file=sink)
                    print(resp, file=sink)
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("channel_name")
    parser.add_argument("user_id")
    args = parser.parse_args()
    today = datetime.now().strftime("%d-%m-%Y")
    log = f"../TwitchChat/logging/chat/{args.channel_name}_{today}.log"
    i = 2
    while Path(log).is_file():
        log = f"../TwitchChat/logging/chat/{args.channel_name}_{today}_{i}.log"
        i += 1
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S',
        handlers=[
            logging.FileHandler(log, encoding='utf-8')
        ]
    )
    main(args)
