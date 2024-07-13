import asyncio
import importlib
import logging

import numpy as np
import pandas as pd
from models import PhishNet
from services.data import load_emails
from sklearn.metrics import confusion_matrix, roc_auc_score

logger = logging.getLogger(__name__)


def load_net(name: str) -> PhishNet:
    """Loads the given PhishNet model.

    Args:
        name (str): Name of net.

    Returns:
        PhishNet: Loaded model.
    """
    return getattr(importlib.import_module(f"services.phishnets"), name)()


def evaluate_phishnet(net_name: str, train: bool, reset: bool, batchsize: int):
    logger.info("Loading phishnet...")
    phishnet = load_net(net_name)
    traindata = load_emails()

    # reset net
    if reset:
        logger.info("Resetting...")
        phishnet.reset()

    # train net
    if train:
        logger.info("Training...")
        phishnet.train(traindata)

    # evaluate net
    logger.info("Evaluating...")
    y_true = []
    y_pred = []
    for emails in traindata.datasetdict["test"].iter(batchsize):
        y_true.extend(emails["label"])
        predictions = asyncio.run(phishnet.analyze(emails))
        y_pred.extend(predictions)
        print_performances(y_true, y_pred)

    print_performances(y_true, y_pred)


def print_performances(y_true: list[float], y_pred: list[float]):
    cmatrix = confusion_matrix(y_true, np.where(np.array(y_pred) >= 0.5, 1, 0))
    auroc = roc_auc_score(y_true, y_pred, labels=[0, 1])
    precision = cmatrix[1, 1] / np.sum(cmatrix[:, 1])  # TP / TP + FP
    recall = cmatrix[1, 1] / np.sum(cmatrix[1, :])  # TP / TP + FN
    fpr = cmatrix[0, 1] / np.sum(cmatrix[0, :])  # FP / FP + TN
    accuracy = (cmatrix[1, 1] + cmatrix[0, 0]) / np.sum(cmatrix)

    print("\n--------Evaluations--------")
    print(f"Accuracy:   {accuracy:.4f}")
    # higher auroc means higher accuracy and confidence
    print(f"AUROC:      {auroc:.4f}")
    # higher precision means we less frequently mark an email incorrectly as phishing
    print(f"Precision:  {precision:.4f}")
    # higher recall means we let less phishing emails get through
    print(f"Recall:     {recall:.4f}")
    # lower FPR means we less frequently mark an email incorrectly as phishing
    print(f"FPR:        {fpr:.4f}")

    # confusion table
    cmatrix_table = pd.DataFrame(
        data={
            "|  ": ["Predicted| N", "Class| P"],
            "N": cmatrix[0, :],
            "P": cmatrix[1, :],
        }
    ).to_string(index=False)
    print(f"            True Class\n          ____________\n{cmatrix_table}")
