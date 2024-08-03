from dataclasses import dataclass

from datasets import IterableDatasetDict


@dataclass
class TrainData:
    datasetdict: IterableDatasetDict
    metadata: dict
