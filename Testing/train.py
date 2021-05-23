#!/usr/bin/env python

import argparse
import gensim
import itertools
import json
import os
import pickle
import re

import pandas as pd
import numpy as np

from sklearn.naive_bayes import MultinomialNB
#from sklearn.linear_model import LogisticRegression

clf1 = MultinomialNB()
#clf2 = SGDClassifier()
#clf3 = LogisticRegression(random_state=0, warm_start=True)

clfs = {
    "nb": clf1
}

def chunked_iterable(iterable, size):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk

def preprocess_data(messages, tags, best_words, vocab, tag_id, using_pmi):
    all_vectors = []
    all_tag_ids = []
    for i in range(len(messages)):
        text = messages[i]
        emote = tags[i]
        tokenized_sent = set(text.split())
        sent_vec = []
        if using_pmi == "False":
            for word in vocab:
                if word != emote.lower():
                    if word in tokenized_sent:
                        sent_vec.append(1)
                    else:
                        sent_vec.append(0)
        else:
            for word in best_words:
                if word in tokenized_sent:
                    sent_vec.append(1)
                else:
                    sent_vec.append(0)
        all_vectors.append(sent_vec)
        idx = tag_id[emote]
        all_tag_ids.append(idx)
    return all_vectors, all_tag_ids

def preprocess_tags(tag_list, tag_id):
    all_tag_ids = []
    for i in range(len(tag_list)):
        emote = tag_list[i]
        idx = tag_id[emote]
        all_tag_ids.append(idx)
    return all_tag_ids

def get_vocab(pmi_json):
    vocab = set()
    first_emote, words = next(iter(pmi_json.items()))
    for key in words.keys():
        vocab.add(key)
    return vocab

"""
def train_and_predict(clfs, training_messages, training_tags, testing_messages, testing_tags, testing_all_tags, best_words, vocab, tag_id, id_tag, classes, file_name):
    for string, clf in clfs.items():
        i = 0
        while i < len(training_messages):
            if i + 100000 >= len(training_messages):
                j = len(training_messages) - 1
            else:
                j = i + 100000
            X_train, y_train, X_train_pmi = preprocess_data(training_messages[i:j], training_tags[i:j], best_words, vocab, tag_id)
            i += 100000
            clf_non_pmi.partial_fit(X_train, y_train, classes=classes)
            clf_pmi.partial_fit(X_train_pmi, y_train, classes=classes)
        X_test, y_test, X_test_pmi = preprocess_data(testing_messages, testing_tags, best_words, vocab, tag_id)
        with open(f"../Testing/predictions/{file_name}{string}.tsv", "w") as sink:
            print("Message\tPrediction\tEmote\tEmotes", file=sink)
            for i in range(len(X_test)):
                prediction = clf.predict([X_test[i]])[0]
                print(f"{testing_messages[i]}\t{id_tag[prediction]}\t{id_tag[y_test[i]]}\t{testing_all_tags[i]}", file=sink)
        with open(f"../Testing/predictions/{file_name}{string}-pmi.tsv", "w") as sink:
            print("Message\tPrediction\tEmote\tEmotes", file=sink)
            for i in range(len(X_test_pmi)):
                prediction = clf_pmi.predict([X_test_pmi[i]])[0]
                print(f"{testing_messages[i]}\t{id_tag[prediction]}\t{id_tag[y_test[i]]}\t{testing_all_tags[i]}", file=sink)
"""

def main(args):
    file_name = re.match("^.*/(.*?).tsv", args.file_name).group(1)
    scope = int(args.scope)
    using_pmi = args.pmi
    with open(f"../Testing/pmi/{file_name}-{scope}.json", "r") as source:
        pmi_json = json.load(source)
    with open(f"../Testing/word-counts/{file_name}-{scope}.json", "r") as source:
        word_counts = json.load(source)
    vocab = {k for k, v in word_counts.items()}
    best_words = []
    for emote, pmis in pmi_json.items():
        ordered_pmis = {k:v for k, v in sorted(pmis.items(), key=lambda item: item[1], reverse=True)}
        best_100 = list(ordered_pmis.items())[:100]
        for word, pmi in best_100:
            best_words.append(word)
    best_words = sorted(set(best_words))
    df = pd.read_csv(args.file_name, sep="\t")
    df = df[df["Scope"]==0]
    training = df[df["Training"]==True]
    training_messages = training["Text"].tolist()
    training_tags = training["Emote"].tolist()
    tag_set = set(df["Emote"].tolist())
    testing = df[df["Training"]==False]
    testing_messages = testing["Text"].tolist()
    testing_tags = testing["Emote"].tolist()
    testing_all_tags = testing["Emotes"].tolist()
    i = 0
    tag_id = {}
    id_tag = {}
    for tag in tag_set:
        i += 1
        tag_id[tag] = i
        id_tag[i] = tag
    classes = [k for k in id_tag.keys()]
    i = 0
    print("Preprocessing test data")
    X_test, y_test = preprocess_data(testing_messages, testing_tags, best_words, vocab, tag_id, using_pmi)
    print("Done")
    while i < len(training_messages):
        if i + 10000 >= len(training_messages):
            j = len(training_messages) - 1
        else:
            j = i + 10000
        print("Preprocessing training data")
        X_train, y_train = preprocess_data(training_messages[i:j], training_tags[i:j], best_words, vocab, tag_id, using_pmi)
        print("done")
        i += 10000
        for string, clf in clfs.items():
            try:
                print("Fitting clf")
                clf.partial_fit(X_train, y_train, classes=classes)
                print("done")
            except AttributeError:
                clf.fit(X_train, y_train)
    if using_pmi == "False":
        prediction_path = f"../Testing/predictions/{file_name}-{string}-{scope}-2.tsv"
    else:
        prediction_path = f"../Testing/predictions/{file_name}-{string}-{scope}-pmi-2.tsv"
    print("Predicting")
    with open(prediction_path, "w") as sink:
        print("Message\tPrediction\tEmote\tEmotes", file=sink)
        for i in range(len(X_test)):
            prediction = clf.predict([X_test[i]])[0]
            print(f"{testing_messages[i]}\t{id_tag[prediction]}\t{id_tag[y_test[i]]}\t{testing_all_tags[i]}", file=sink)
    """
    for chunk in chunked_iterable(training, 100000):
        X_train, y_train = preprocess_data(training_messages, training_tags, best_words, vocab, tag_id)
        print("fitting")
        clf.partial_fit(X_train, y_train, classes=classes)
    testing = df[df["Training"]==False]
    testing_messages = testing["Text"].tolist()
    testing_tags = testing["Emote"].tolist()
    testing_all_tags = testing["Emotes"].tolist()
    X_test, y_test = preprocess_data(testing_messages, testing_tags, best_words, tag_id)
    with open(f"../Testing/predictions/{file_name}.tsv", "w") as sink:
        print("Message\tPrediction\tEmote\tEmotes", file=sink)
        for i in range(len(X_test)):
            prediction = clf.predict([X_test[i]])[0]
            print(f"{testing_messages[i]}\t{id_tag[prediction]}\t{id_tag[y_test[i]]}\t{testing_all_tags[i]}", file=sink)
    """
    #prediction = clf.predict([X_train[2]])[0]
    #print(id_tag[prediction])
    #print(id_tag[y_train[2]])



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("file_name")
    parser.add_argument("scope")
    parser.add_argument("--pmi", default=False)
    args = parser.parse_args()
    main(args)
