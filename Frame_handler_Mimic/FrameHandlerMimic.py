import json
import multiprocessing as mp
import time

import numpy as np

from Frame_handler_Mimic.IFrameHandler import IFrameHandler
# from Mimic_Analyzer.MimicAnalyzer import MimicAnalyzer
from Mimic_Analyzer.MimicAnalyzerOpenface import MimicAnalyzer


class FrameHandlerMimic(IFrameHandler):
    def __init__(self, path='mimic.json'):
        """
        Инициализатор
        :param path: Название файла для передачи между процессами
        """
        self.__path = path
        self.__queue = mp.Queue()
        self.__process = mp.Process(target=self._frame_handler, args=(self.__queue, self.__path))

    @staticmethod
    def _frame_handler(queue, path):
        """
        Метод параллельной обработки кадров
        :param queue: Очередь, в которую будут складываться кадры
        :return: None
        """
        mimic_analyzer = MimicAnalyzer()
        results = []
        while True:
            # Если в очереди нет кадров продолжи ожидать
            if queue.empty():
                continue

            frame = queue.get()

            # Проверка на конец регистрации
            if frame is None:
                break

            result = mimic_analyzer.process_frame(frame)
            results.append(result)

        with open(path, 'w') as file:
            json.dump(results, file)

    def start(self):
        """
        Метод запуска процесса обработки кадров
        """
        self.__process.start()

    def push(self, frame: np.ndarray):
        """
        Метод для отправки кадров на обработку
        :param frame: Кадр или None в виде стоп кадра
        """
        self.__queue.put(frame)

    def finish(self):
        """
        Метод, который говорит о том, что кадров больше не будет.
        (Сам отправит None)
        """
        self.__queue.put(None)

    def join(self, timeout=1) -> list:
        """
        Метод ожидания завершения процесса обработки
        :param timeout: время ожидания завершения (В секундах)
        :return: Массив результатов распознавания мимики
        """
        while True:
            time.sleep(1)
            if self.__queue.qsize() == 0:
                self.__process.join(timeout=timeout)
                break

        results = []
        # Получение результатов распознавания мимики
        with open(self.__path, 'r') as file:
            results = json.load(file)
        return results

    def is_alive(self) -> bool:
        """
        Метод проверки на завершения процесса
        :return: True - если процесс всё ещё идёт иначе False
        """
        return self.__process.is_alive()