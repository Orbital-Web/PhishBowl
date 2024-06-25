from phishnet.PhishNet import Email
from zipfile import ZipFile
import csv
import os
from typing import Iterator

csv.field_size_limit(0xFFFFFF)  # max 0x7FFFFFFF


def load() -> Iterator[Email]:
    path = "phishnet/dataset/"
    dataset = "CuratedDataset"

    # extract if necessary
    if not os.path.exists(f"{path}{dataset}.zip"):
        raise FileNotFoundError(
            f"Please make sure to download {path}{dataset}.zip from https://figshare.com/articles/dataset/Curated_Dataset_-_Phishing_Email/24899952"
        )

    with ZipFile(f"{path}{dataset}.zip", "r") as zipfile:
        if not os.path.exists(f"{path}{dataset}"):
            print("Extracting dataset...")
            zipfile.extractall(path)

    # load dataset
    print("Loading dataset CEAS_08...")
    with open(f"{path}{dataset}/CEAS_08.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 6 or not row[4]:
                continue
            yield Email(subject=row[3], sender=row[0], body=row[4], phish_score=row[5])

    print("Loading dataset Enron...")
    with open(f"{path}{dataset}/Enron.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 3 or not row[1]:
                continue
            yield Email(subject=row[0], body=row[1], phish_score=row[2])

    print("Loading dataset SpamAssasin...")
    with open(f"{path}{dataset}/SpamAssasin.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 6 or not row[4]:
                continue
            yield Email(subject=row[3], sender=row[0], body=row[4], phish_score=row[5])

    print("Loading dataset Ling...")
    with open(f"{path}{dataset}/Ling.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if len(row) < 3 or not row[1]:
                continue
            yield Email(subject=row[0], body=row[1], phish_score=row[2])

    print("Loading dataset TREC...")
    for i in (5, 6, 7):
        with open(f"{path}{dataset}/TREC_0{i}.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            for row in reader:
                if len(row) < 6 or not row[4]:
                    continue
                yield Email(
                    subject=row[3], sender=row[0], body=row[4], phish_score=row[5]
                )
