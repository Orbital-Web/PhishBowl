from phishnet.PhishNet import PhishNet, Email
import argparse
import importlib
from sklearn.metrics import confusion_matrix, roc_auc_score
import numpy as np
from typing import Callable, Iterator

LoaderType = Callable[[], Iterator[Email]]


def LoadNet(name: str) -> PhishNet:
    """Loads the given PhishNet model.

    Args:
        name (str): Name of net.

    Returns:
        PhishNet: Loaded model.
    """
    return getattr(importlib.import_module(f"phishnet.nets.{name}"), name)()


def LoadDatasetLoader(name: str) -> LoaderType:
    """Loads the given dataset loader.

    Args:
        name (str): Name of dataset.

    Returns:
        list[Email]: Loaded emails.
    """
    return importlib.import_module(f"phishnet.dataset.load_{name}").load


def EvaluatePhishNet(phishnet: PhishNet, loader: LoaderType):
    y_true = []
    y_pred = []

    for email in loader():
        y_true.append(email.phish_score)
        prediction = phishnet.rateEmail(email)
        y_pred.append(prediction)

    cmatrix = confusion_matrix(y_true, np.where(np.array(y_pred) >= 0.5, 1, 0))
    auroc = roc_auc_score(y_true, y_pred, labels=[0, 1])
    precision = cmatrix[1, 1] / np.sum(cmatrix[:, 1])  # TP / TP + FP
    recall = cmatrix[1, 1] / np.sum(cmatrix[1, :])  # TP / TP + FN
    accuracy = (cmatrix[1, 1] + cmatrix[0, 0]) / np.sum(cmatrix)

    print("\n--------Evaluations--------")
    print(f"Accuracy:  {accuracy:.4f}")
    # higher auroc means higher accuracy and confidence
    print(f"AUROC:     {auroc:.4f}")
    # higher precision means we less frequently mark an email incorrectly as phishing
    print(f"Precision: {precision:.4f}")
    # higher recall means we let less phishing emails get through
    print(f"Recall:    {recall:.4f}")
    # row: truth, columns: predicted
    print(f"Confusion Matrix:\n{cmatrix}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--net",
        type=str,
        default="SemanticSearchPhishNet",
        help="Name of the net to use",
    )
    parser.add_argument(
        "-d",
        "--dataset",
        type=str,
        default="curated",
        help="Name of the dataset to use",
    )
    args = parser.parse_args()

    phishnet = LoadNet(args.net)
    loader = LoadDatasetLoader(args.dataset)
    EvaluatePhishNet(phishnet, loader)
