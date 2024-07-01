from datasets import DatasetDict, Dataset
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)


def load_emails(
    test_split: float = 0.2, shuffle: bool = True, consistent_splits: bool = True
) -> DatasetDict:
    """Loads all the emails and returns a dataset split into training and testing data.

    Args:
        test_split (float, optional): Ratio of dataset to use for testing. Defaults to
            0.2.
        shuffle (bool, optional): Whether to shuffle the dataset. Defaults to False.
        consistent_splits (bool, optional): If True, it will shuffle the dataset after
            splitting, thus making every split consistent. If False, it will shuffle
            before splitting, resulting in a new split each time. Defaults to True.

    Returns:
        DatasetDict: The generated dataset.
    """
    PATH = "services/data/curated/"
    FILES = [
        f"{PATH}CEAS_08.csv",
        f"{PATH}Enron.csv",
        f"{PATH}Nazario_5.csv",
        f"{PATH}Nigerian_5.csv",
        f"{PATH}SpamAssasin.csv",
        f"{PATH}TREC_05.csv",
        f"{PATH}Ling.csv",
        f"{PATH}TREC_06.csv",
        f"{PATH}TREC_07.csv",
    ]
    FEATURES = ["sender", "subject", "body", "label"]

    logger.info("Loading dataset...")

    # validate files exists
    for filepath in FILES:
        if not os.path.exists(filepath):
            raise FileNotFoundError(
                f"Missing file {filepath}! Make sure to download and extract the files from:\n"
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
    dataset = dataset.train_test_split(
        test_size=test_split, shuffle=shuffle and not consistent_splits
    )
    if shuffle and consistent_splits:
        dataset["train"] = dataset["train"].shuffle()
        dataset["test"] = dataset["test"].shuffle()

    logger.info(f"Generated dataset:\n{dataset}")
    return dataset
