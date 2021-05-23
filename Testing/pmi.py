#!/usr/bin/env python

import argparse
import enchant
import json
import re

from math import log2

def pmi(p_x, p_y, p_xy):
    p_x_n, p_x_d = p_x
    p_y_n, p_y_d = p_y
    p_xy_n, p_xy_d = p_xy
    return log2((p_xy_n/p_xy_d) / ((p_x_n/p_x_d) * (p_y_n/p_y_d)))

def string_to_ratio(string):
    num = int(re.match("^([0-9]*)/.*$", string).group(1))
    den = int(re.match("^.*/([0-9]*)$", string).group(1))
    fraction = (num/den).as_integer_ratio()
    return(fraction)

def main(args):
    #en_d = enchant.Dict("en_US")
    file_name = re.match("^.*/(.*?).json", args.file_name).group(1)
    with open(f"../Testing/word-counts/{file_name}.json", "r") as source:
        word_counts = json.load(source)
    with open(f"../Testing/emote-counts/{file_name}.json", "r") as source:
        emote_counts = json.load(source)
    with open(args.file_name, "r") as source:
        collocations = json.load(source)
        #d_words = full_json["words"]
        #d_emotes = full_json["emotes"]
    num_docs = collocations["TOTAL_COUNT"]
    d_pmi = {}
    for pair, count in collocations.items():
        if pair != "TOTAL_COUNT":
            emote, word = pair.split(": ")
            emote_count = emote_counts[emote]
            word_count = word_counts[word]
            if count != 0:
                coocurrence_prob = (count/num_docs).as_integer_ratio()
                word_prob = (word_count/num_docs).as_integer_ratio()
                emote_prob = (emote_count/num_docs).as_integer_ratio()
                if emote not in d_pmi.keys():
                    d_pmi[emote] = {}
                d_pmi[emote][word] = pmi(word_prob, emote_prob, coocurrence_prob)
        """
        emote_prob = string_to_ratio(info["ratio"])
        for word, value in info["words"].items():
            if value["count"] >= 20:
                coocurrence_prob = string_to_ratio(value["ratio"])
                word_prob = string_to_ratio(d_words[word]["ratio"])
                if emote not in d_pmi.keys():
                    d_pmi[emote] = {}
                #d_pmi[(word, emote)]["word_probability"] = word_probability
                #d_pmi[(word, emote)]["coocurrence_prob"] = coocurrence_prob
                #d_pmi[(word, emote)]["emote_prob"] = emote_prob
                d_pmi[emote][word] = pmi(word_prob, emote_prob, coocurrence_prob)
        """
    with open(f"../Testing/pmi/{file_name}.json", "w") as sink:
        json.dump(d_pmi, sink)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    args = parser.parse_args()
    main(args)
