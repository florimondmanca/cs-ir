import math


def e_measure(precision: float, recall: float, alpha: float = 0.5) -> float:
    return 1 - 1 / (alpha / precision + (1 - alpha) / recall)


def f_measure(precision: float, recall: float, alpha: float = 0.5) -> float:
    return 1 - e_measure(precision, recall, alpha=alpha)
