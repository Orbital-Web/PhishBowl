from phishnet.PhishNet import PhishNet
from phishnet.dataset.loader import load
import argparse
import importlib
from sklearn.metrics import confusion_matrix, roc_auc_score
import numpy as np
import logging

logger = logging.getLogger(__name__)


def LoadNet(name: str) -> PhishNet:
    """Loads the given PhishNet model.

    Args:
        name (str): Name of net.

    Returns:
        PhishNet: Loaded model.
    """
    return getattr(importlib.import_module(f"phishnet.nets.{name}"), name)()


def EvaluatePhishNet(phishnet: PhishNet, train: bool, batchsize: int):
    y_true = []
    y_pred = []

    dataset = load(shuffle=False)

    # train net
    if train:
        logger.info("Training...")
        phishnet.reset()
        phishnet.train(dataset)

    # evaluate
    logger.info("Evaluating...")
    for i in range(0, dataset["test"].num_rows, batchsize):
        batch = dataset["test"][i : i + batchsize]
        y_true.extend(batch["label"])
        predictions = phishnet.rateEmails(batch)
        y_pred.extend(predictions)
        if i % 4096 < batchsize:
            printStats(y_true, y_pred)

    printStats(y_true, y_pred)


def printStats(y_true: list[float], y_pred: list[float]):
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
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--net",
        type=str,
        default="SemanticSearchPhishNet",
        help="Name of the net to use",
    )
    parser.add_argument(
        "-t",
        "--train",
        default=False,
        help="Whether to train the net",
        action="store_true",
    )
    parser.add_argument(
        "-b",
        "--batchsize",
        type=int,
        default=128,
        help="Number of emails to process at once",
    )
    args = parser.parse_args()

    phishnet = LoadNet(args.net)
    EvaluatePhishNet(phishnet, args.train, args.batchsize)
