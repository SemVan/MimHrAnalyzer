import numpy as np
from abc import ABC, abstractmethod


class IFrameHandler(ABC):
    @abstractmethod
    def __init__(self, path: str):
        """
        Инициализатор
        :param path: Название файла для передачи между процессами
        """
        pass

    @abstractmethod
    def start(self):
        """
        Метод запуска процесса обработки кадров
        """
        pass

    @abstractmethod
    def push(self, frame: np.ndarray):
        """
        Метод для отправки кадров на обработку
        :param frame: Кадр или None в виде стоп кадра
        """
        pass

    @abstractmethod
    def finish(self):
        """
        Метод, который говорит о том, что кадров больше не будет.
        (Сам отправит None)
        """
        pass

    @abstractmethod
    def join(self, timeout=None):
        """
        Метод ожидания завершения процесса обработки
        :param timeout: время ожидания завершения (В секундах)
        :return: Объект с обработанными кадрами
        """
        pass

    @abstractmethod
    def is_alive(self) -> bool:
        """
        Метод проверки на завершения процесса
        :return: True - если процесс всё ещё идёт иначе False
        """
        pass