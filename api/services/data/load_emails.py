from datasets import (
    Dataset,
    IterableDatasetDict,
    load_dataset,
)
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def preload_emails(savepath: str, test_ratio: float = 0.2, shuffle: bool = True):
    """Preloads all the emails into memory, splits into test and training data, and
    saves it under `savepath` as 2 csv files. Run this once to preload the emails so
    that they can be lazily loaded in the future, reducing the memory footprint.
    Note that preloading the emails multiple times will result in a different split
    each time.

    Args:
        savepath (str): Path to save the preloaded dataset to.
        test_ratio (float, optional): Ratio of dataset to use as the test split.
            Defaults to 0.2.
        shuffle (bool, optional): Whether to shuffle the dataset first before splitting.
            Defaults to True.
    """
    LOADPATH = "/app/services/data/curated/"
    FILES = [
        f"{LOADPATH}CEAS_08.csv",
        f"{LOADPATH}Enron.csv",
        f"{LOADPATH}Nazario_5.csv",
        f"{LOADPATH}Nigerian_5.csv",
        f"{LOADPATH}SpamAssasin.csv",
        f"{LOADPATH}TREC_05.csv",
        f"{LOADPATH}Ling.csv",
        f"{LOADPATH}TREC_06.csv",
        f"{LOADPATH}TREC_07.csv",
    ]
    FEATURES = ["sender", "subject", "body", "label"]

    logger.info("Building dataset...")

    # validate files exists
    for filepath in FILES:
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Missing file {filepath}! Make sure to download the files from:\n"
                + "  https://figshare.com/articles/dataset/Curated_Dataset_-_Phishing_Email/24899952\n"
                + "  https://figshare.com/articles/dataset/Phishing_Email_11_Curated_Datasets/24952503\n"
            )

    # load and merge files into a single dataframe
    dfs = [pd.read_csv(filepath, lineterminator="\n") for filepath in FILES]
    df = pd.concat(dfs, join="outer", ignore_index=True)[FEATURES]
    df.fillna({"sender": "", "subject": ""}, inplace=True)
    df.dropna(inplace=True)  # ignore those missing label or body
    df.drop_duplicates(inplace=True)

    # create dataset
    dataset = Dataset.from_pandas(df, preserve_index=False)
    datasetdict = dataset.train_test_split(test_size=test_ratio, shuffle=shuffle)

    logger.info("Saving dataset to disc...")
    datasetdict["train"].to_csv(f"{savepath}/train.csv")
    datasetdict["test"].to_csv(f"{savepath}/test.csv")


def load_emails(test_ratio: float = 0.2, shuffle: bool = True) -> IterableDatasetDict:
    """Lazily loads all the emails as an iterable datasetdict.

    Args:
        test_ratio (float, optional): Ratio of dataset to use as the test split.
            Defaults to 0.2.
        shuffle (bool, optional): Whether to shuffle the training and testing datasets.
            Note that it only shuffles emails in the buffer. Defaults to True.

    Returns:
        IterableDatasetDict: The loaded datasetdict.
    """
    LOADPATH = "/app/services/data/"
    TRAINFILE = f"{LOADPATH}train.csv"
    TESTFILE = f"{LOADPATH}test.csv"

    # preload emails if they haven't been loaded before.
    # note that this will use a lot of memory.
    if not os.path.exists(TRAINFILE) or not os.path.exists(TESTFILE):
        preload_emails(LOADPATH, test_ratio, shuffle=True)

    # lazy load the dataset from disc.
    # this will not use as much memory, granted preload was not called.
    logger.info("Loading dataset...")
    datasetdict = load_dataset(
        "csv", data_files={"train": TRAINFILE, "test": TESTFILE}, streaming=True
    )
    if shuffle:
        datasetdict = datasetdict.shuffle(buffer_size=1024)
    return datasetdict
