import json
import multiprocessing as mp

import numpy as np

from Frame_handler.IFrameHandler import IFrameHandler
from VPG_Generator.VPGGenerator import VPGGenerator


class FrameHandlerVPG(IFrameHandler):
    def __init__(self, path='vpg.json'):
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
        vpg_generator = VPGGenerator()
        vpg = []
        while True:
            # Если в очереди нет кадров продолжи ожидать
            if queue.empty():
                continue

            frame = queue.get()

            # Проверка на конец регистрации
            if frame is None:
                break

            value = vpg_generator.get_vpg_discret(frame)
            # value = vpg_generator.get_vpg_discret_without_face(frame)
            vpg.append(value)

        with open(path, 'w') as file:
            json.dump(vpg, file)

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

    def join(self, timeout=None) -> list:
        """
        Метод ожидания завершения процесса обработки
        :param timeout: время ожидания завершения (В секундах)
        :return: Массив ВПГ (Не фильтрованный)
        """
        self.__process.join(timeout=timeout)
        vpg = []
        # Получение сигнала ВПГ
        with open(self.__path, 'r') as file:
            vpg = json.load(file)
        return vpg

    def is_alive(self) -> bool:
        """
        Метод проверки на завершения процесса
        :return: True - если процесс всё ещё идёт иначе False
        """
        return self.__process.is_alive()