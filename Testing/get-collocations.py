#!/usr/bin/env python

import argparse
import json
import os
import re

import pandas as pd

mpa = dict.fromkeys(range(32))

def remove_quotes(word):
    word = re.sub("'", "", word)
    word = re.sub('"', "", word)
    return word

def main(args):
    scope = int(args.scope)
    smoothing = int(args.smoothing)
    #emote_folder = os.path.join(os.path.dirname(__file__), '..', 'data/emotes')
    #emote_file = os.path.join(emote_folder, "all_emotes.json")
    #with open(emote_file, "r") as source:
        #emote_json = json.load(source)
    #d_words = {}
    #d_emotes = {}
    d_counts = {}
    word_counts = {}
    emote_counts = {}
    num_docs = 0
    with open(args.file_name, "r") as source:
        line = source.readline().rstrip().split('\t')
        line = source.readline()
        while line:
            line = line.rstrip().split('\t')
            try:
                if int(line[5]) == scope:
                    message = line[1]
                    emote = line[2]
                    emotes = line[3]
                    is_training = line[4]
                    words = set(message.split())
                    if emote not in emote_counts.keys():
                        emote_counts[emote] = 0
                    for word in words:
                        if f"{emote}: {word}" not in d_counts.keys():
                            d_counts[f"{emote}: {word}"] = 0
                        if word not in word_counts.keys():
                            word_counts[word] = 0
                    if is_training != "False":
                        num_docs += 1
                        for word in words:
                            d_counts[f"{emote}: {word}"] += 1
                            word_counts[word] += 1
                            emote_counts[emote] += 1
                        """
                        if emote in d_emotes.keys():
                            d_emotes[emote]["count"] += 1
                        else:
                            d_emotes[emote] = {}
                            d_emotes[emote]["count"] = 1
                            d_emotes[emote]["words"] = {}
                        for word in words:
                            #if word is not emote:
                            if word in d_words.keys():
                                d_words[word]["count"] += 1
                            else:
                                d_words[word] = {}
                                d_words[word]["count"] = 1
                            if word != emote:
                                if word in d_emotes[emote]["words"].keys():
                                    d_emotes[emote]["words"][word]["count"] += 1
                                else:
                                    d_emotes[emote]["words"][word] = {}
                                    d_emotes[emote]["words"][word]["count"] = 1
                        """
            except:
                print(line)
                assert False
            line = source.readline()
        d_counts["TOTAL_COUNT"] = num_docs
    """
    if args.mode == "message":
        print("getting collocations by message")
        stream_messages = df["Text"].tolist()
        stream_emotes = df["Emote"].tolist()
        is_training = df["Training"].tolist()
        for i in range(num_docs):
            emote = stream_emotes[i]
            messages = stream_messages[i]
            words = set(messages.split())
            for word in words:
                vocab.add(word)
            if is_training[i]:
                if emote in d_emotes.keys():
                    d_emotes[emote]["count"] += 1
                else:
                    d_emotes[emote] = {}
                    d_emotes[emote]["count"] = 1
                    d_emotes[emote]["words"] = {}
                for word in words:
                    #if word is not emote:
                    if word in d_words.keys():
                        d_words[word]["count"] += 1
                    else:
                        d_words[word] = {}
                        d_words[word]["count"] = 1
                    if word != emote:
                        if word in d_emotes[emote]["words"].keys():
                            d_emotes[emote]["words"][word]["count"] += 1
                        else:
                            d_emotes[emote]["words"][word] = {}
                            d_emotes[emote]["words"][word]["count"] = 1
    """
    """
    for emote in d_emotes.keys():
        for word in vocab:
            if word not in d_emotes[emote]["words"].keys():
                d_emotes[emote]["words"][word] = {}
                d_emotes[emote]["words"][word]["count"] = 0
                d_emotes[emote]["words"][word]["probability"] = 0
                d_emotes[emote]["words"][word]["ratio"] = (0, num_docs)
        for key, value in d_emotes[emote]["words"].items():
            if smoothing:
                value["count"] += smoothing
                d_words[key]["count"] += smoothing
                d_emotes[emote]["count"] += smoothing
            value["ratio"] = f'{value["count"]}/{num_docs}'
            value["probability"] = value["count"]/num_docs
        d_emotes[emote]["ratio"] = f'{d_emotes[emote]["count"]}/{num_docs}'
        d_emotes[emote]["probability"] = d_emotes[emote]["count"]/num_docs
    for word, info in d_words.items():
        info["ratio"] = f'{info["count"]}/{num_docs}'
        info["probability"] = info["count"]/num_docs
        """
    """
        for emote, value in d_emotes.items():
            if word not in value["words"].keys():
                d_emotes[emote]["words"][word] = {}
                d_emotes[emote]["words"][word]["count"] = 0
                d_emotes[emote]["words"][word]["probability"] = 0
                d_emotes[emote]["words"][word]["ratio"] = (0, df_length)
    """
    #full_d = {}
    #full_d["words"] = d_words
    #full_d["emotes"] = d_emotes
    file_name = re.match("^.*/(.*?).tsv", args.file_name).group(1)
    with open(f"../Testing/collocations/{file_name}-{scope}.json", "w") as sink:
        json.dump(d_counts, sink)
    with open(f"../Testing/word-counts/{file_name}-{scope}.json", "w") as sink:
        json.dump(word_counts, sink)
    with open(f"../Testing/emote-counts/{file_name}-{scope}.json", "w") as sink:
        json.dump(emote_counts, sink)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("mode")
    parser.add_argument("scope")
    parser.add_argument("--smoothing", default=False)
    args = parser.parse_args()
    main(args)
