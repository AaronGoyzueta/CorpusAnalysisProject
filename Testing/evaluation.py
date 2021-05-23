#!/usr/bin/env python

import argparse
import ast
import re

import pandas as pd

def main(args):
    file_name = re.match("^.*/(.*?).tsv", args.file_name).group(1)
    df = pd.read_csv(args.file_name, sep='\t')
    results = {
    }
    overall = {
        "correct": 0,
        "incorrect": 0,
        "total": 0,
        "accuracy": 0
    }
    for i in range(len(df)):
        row = df.loc[i]
        prediction = row["Prediction"]
        emote = row["Emote"]
        emotes = row["Emotes"]
        emotes = ast.literal_eval(emotes)
        if len(emotes) == 1:
            if emote not in results.keys():
                results[emote] = {
                    "count": 0,
                    "TP": 0,
                    "FP": 0,
                    "FN": 0,
                    "Precision": 0,
                    "Recall": 0,
                    "F1": 0
                }
            if prediction not in results.keys():
                results[prediction] = {
                    "count": 0,
                    "TP": 0,
                    "FP": 0,
                    "FN": 0,
                    "Precision": 0,
                    "Recall": 0,
                    "F1": 0
                }
            if prediction == emote:
                results[emote]["TP"] += 1
                overall["correct"] += 1
            else:
                results[emote]["FN"] += 1
                results[prediction]["FP"] += 1
                overall["incorrect"] += 1
            results[emote]["count"] += 1
            overall["total"] += 1
    accuracy = ( overall["correct"]  ) / overall["total"] * 100
    overall["accuracy"] = accuracy
    for key, value in results.items():
        try:
            precision = value["TP"] / ( value["TP"] + value["FP"] )
        except ZeroDivisionError:
            precision = "NA"
        try:
            recall = value["TP"] / ( value["TP"] + value["FN"] )
        except ZeroDivisionError:
            recall = "NA"
        try:
            F1 = ( 2 * precision * recall ) / ( precision + recall )
        except (ZeroDivisionError, TypeError):
            F1 = "NA"
        value["Precision"] = precision
        value["Recall"] = recall
        value["F1"] = F1
    temp = []
    for key, value in results.items():
        temp.append({"Emote": key, "Count": value["count"], "Precision": value["Precision"], "Recall": value["Recall"], "F1": value["F1"]})
    df_results = pd.DataFrame(temp, columns = ["Emote", "Count", "Precision", "Recall", "F1"])
    sorted_df = df_results.sort_values(by=["Count"], ascending=False)
    sorted_df.loc[len(sorted_df.index)] = ["OVERALL_DATA", overall["total"], overall["correct"], overall["incorrect"], overall["accuracy"]]
    #sorted_df.append({"Emote": "OVERALL_DATA", "Count": overall["total"], "Precision": overall["correct"], "Recall": overall["incorrect"], "F1": overall["accuracy"]}, ignore_index=True)
    sorted_df.to_csv(f"../Testing/results/{file_name}.tsv", mode="w", header=True, sep='\t')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    args = parser.parse_args()
    main(args)
