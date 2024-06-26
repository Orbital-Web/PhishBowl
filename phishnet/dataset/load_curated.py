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
    if not os.path.exists(f"{path}{dataset}"):
        if not os.path.exists(f"{path}{dataset}.zip"):
            raise FileNotFoundError(
                f"Please make sure to download {path}{dataset}.zip from https://figshare.com/articles/dataset/Curated_Dataset_-_Phishing_Email/24899952"
            )
        with ZipFile(f"{path}{dataset}.zip", "r") as zipfile:
            print("Extracting dataset...")
            zipfile.extractall(path)

    # load dataset
    for file in ("Enron", "Ling"):
        print(f"Loading dataset {file}")

        with open(f"{path}{dataset}/{file}.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header

            for row in reader:
                if len(row) < 3 or not row[1]:
                    continue
                yield Email(subject=row[0], body=row[1], phish_score=row[2])

    for file in ("CEAS_08", "SpamAssasin", "TREC_06", "TREC_07"):
        print(f"Loading dataset {file}")

        with open(f"{path}{dataset}/{file}.csv", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header

            for row in reader:
                if len(row) < 6 or not row[4]:
                    continue
                yield Email(
                    subject=row[3], sender=row[0], body=row[4], phish_score=row[5]
                )
