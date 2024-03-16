from abc import ABC, abstractmethod

import numpy as np


class IMimicAnalyzer(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Метод обработки одного кадра

        :param frame: Кадр

        :return: Словарь со значениями двигательных единиц и эмоций
        """
        return dict()

    @abstractmethod
    def get_report(self, frames: list) -> list:
        """
        Метод обработки последовательности кадров

        :param frames: Список кадров

        :return: Список словарей со значениями двигательных единиц и эмоций
        """
        results = []
        for frame in frames:
            results.append(dict())

        return results
