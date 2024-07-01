from models import PhishNet
from services.data import load_emails
import importlib
from sklearn.metrics import confusion_matrix, roc_auc_score
import numpy as np
import asyncio
import logging

logger = logging.getLogger(__name__)


def load_net(name: str) -> PhishNet:
    """Loads the given PhishNet model.

    Args:
        name (str): Name of net.

    Returns:
        PhishNet: Loaded model.
    """
    return getattr(importlib.import_module(f"services.phishnets"), name)()


def evaluate_phishnet(net_name: str, train: bool, batchsize: int):
    logger.info("Loading phishnet...")
    phishnet = load_net(net_name)
    dataset = load_emails()

    # train net
    if train:
        logger.info("Training...")
        phishnet.reset()
        phishnet.train(dataset)

    # evaluate
    logger.info("Evaluating...")
    y_true = []
    y_pred = []
    for i in range(0, dataset["test"].num_rows, batchsize):
        batch = dataset["test"][i : i + batchsize]
        y_true.extend(batch["label"])
        predictions = asyncio.run(phishnet.rate(batch))
        y_pred.extend(predictions)
        if i % 4096 < batchsize:
            print_performances(y_true, y_pred)

    print_performances(y_true, y_pred)


def print_performances(y_true: list[float], y_pred: list[float]):
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
