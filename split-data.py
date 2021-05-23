#!/usr/bin/env python

import argparse
import json
import re

import pandas as pd

def main(args):
    df = pd.read_csv(args.file_name, sep="\t")
    df = df[df["Clean_Message"].notna()]
    df_by_stream = [pd.DataFrame(y) for x, y in df.groupby("Stream", as_index=False)]
    length = len(df)
    new_i = 0
    first = True
    for stream_df in df_by_stream:
        data_df = pd.DataFrame(columns = ["Text", "Emote", "Emotes", "Training", "Scope"])
        stream_messages = stream_df["Clean_Message"].tolist()
        stream_emotes = stream_df["Emotes"].fillna(0).tolist()
        df_length = len(stream_df)
        for n in range(0, 6):
            scope = n
            for i in range(df_length):
                new_i += 1
                print(new_i)
                if stream_emotes[i] != 0:
                    emotes = re.findall("'([^ ]*?)',", stream_emotes[i])
                    if i < scope:
                        messages = " ".join(stream_messages[0:i+scope+1])
                    elif i >= df_length - (scope-1):
                        messages = " ".join(stream_messages[i-scope:])
                    else:
                        messages = " ".join(stream_messages[i-scope:i+scope+1])
                    messages = messages.lower()
                    for emote in emotes:
                        data_df.loc[len(data_df.index)] = [messages, emote, emotes, True, n]
        df_shuffled=data_df.sample(frac=1).reset_index(drop=True)
        df_len = len(df_shuffled)
        for index in df_shuffled.index:
            if (index + 1) <= df_len/10:
                df_shuffled.loc[index, "Training"] = False
        file_name = re.match("^.*/(.*?).tsv", args.file_name).group(1)
        if first:
            df_shuffled.to_csv(f"../TwitchChat/Testing/train-test-data/{file_name}.tsv", mode="w", header=True, sep='\t')
            first = False
        else:
            df_shuffled.to_csv(f"../TwitchChat/Testing/train-test-data/{file_name}.tsv", mode="a", header=False, sep='\t')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    args = parser.parse_args()
    main(args)
