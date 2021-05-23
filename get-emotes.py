#!/usr/bin/env python

import json
import requests

from bs4 import BeautifulSoup as bs
from urllib.request import urlopen

BASE_URL = 'https://api.twitchemotes.com/api/v4/channels/'
global_emotes_url = "https://twitchemotes.com/"
ffz_emotes_url = "https://www.frankerfacez.com"

def soup(url: str):
    soup_client = urlopen(url)
    soup_html = soup_client.read()
    soup_client.close()
    soup_bs = bs(soup_html, "html.parser")
    return soup_bs

def get_ffz_emotes(page_soup, sink):
    ffz_emotes = page_soup.findAll("tr", {"class": "selectable"})
    for emote in ffz_emotes:
        emote_name_selector = emote.findChild()
        emote_name = emote_name_selector.findChild().text
        print(emote_name, file=sink)

def main():
    with open("../TwitchChat/data/channels.json") as source:
        channel_json = json.load(source)
        channels = channel_json["channels"]
    for channel in channels:
        for channel_name, data in channel.items():
            new_path = f"../TwitchChat/data/emotes/{channel_name}_emotes.json"
            channel_id = data[0]["id"]
            query = BASE_URL + channel_id
            response = requests.get(query)
            with open(new_path, "w") as sink:
                json.dump(response.json(), sink, indent=4)
    global_emotes_soup = soup(global_emotes_url)
    global_emotes = global_emotes_soup.findAll("div", {"class": "col-md-2"})
    with open("../TwitchChat/data/emotes/global_emotes.txt", "w") as sink:
        for emote in global_emotes:
            emote_name = emote.findChild().text
            print(emote_name, file=sink)
    ffz_emotes_soup = soup(ffz_emotes_url + "/emoticons")
    with open("../TwitchChat/data/emotes/ffz_emotes.txt", "w") as sink:
        for i in range(10):
            print(f"FFZ page {i+1}")
            get_ffz_emotes(ffz_emotes_soup, sink)
            for link in ffz_emotes_soup.findAll("a", {"class": "next_page"}):
                new_link = link['href']
            ffz_emotes_soup = soup(ffz_emotes_url + new_link)

if __name__ == "__main__":
    main()
