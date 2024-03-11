import multiprocessing as mp
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time

from VPGGenerator.VPGGenerator import VPGGenerator
from VPGAnalyzer.VPGAnalyzer import VPGAnalyzer


class App:
    def __init__(self):
        self.__queue = mp.Queue()
        self.__frame_handler_process = mp.Process(target=self._frame_handler, args=(self.__queue,))
        self.__vpg = []
        self.__fps = 0

    @staticmethod
    def _frame_handler(queue):
        """
        Метод параллельной обработки кадров
        :param queue: Очерь, в которую будут складываться кадры
        :return:
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
            vpg.append(value)

        queue.put(vpg)

    def _registrate(self):
        self.__frame_handler_process.start()

        cap = cv2.VideoCapture(0)
        self.__fps = cap.get(cv2.CAP_PROP_FPS)

        start = time.time()
        while (True):
            ret, frame = cap.read()

            # Если кадр не считался выйти из цикла
            if ret == False:
                cap.release()
                cv2.destroyAllWindows()
                break

            cv2.imshow('Video', frame)
            self.__queue.put(frame)

            # Если нажата кнопка закончить регистрацию
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cap.release()
                cv2.destroyAllWindows()
                break

        self.__queue.put(None)
        self.__frame_handler_process.join()

        # Получение сигнала ВПГ
        self.__vpg = self.__queue.get()

    def _analyzer(self):
        vpg_analyzer = VPGAnalyzer()

        # Избавление от кадров без лица
        for i in range(len(self.__vpg)):
            if self.__vpg[i] is None:
                if i == 0:
                    self.__vpg[i] = 0
                else:
                    self.__vpg[i] = self.__vpg[i - 1]
        # Нормолизуем сигнал
        self.__vpg = (self.__vpg - np.mean(self.__vpg)) / np.std(self.__vpg)

        plt.plot(self.__vpg)

        # Фильтрация
        self.__vpg = vpg_analyzer.filt(self.__vpg, self.__fps)

        plt.plot(self.__vpg)
        plt.show()

        # Расчёт ЧСС
        print(f'Длинна сигнала: {len(self.__vpg)}')
        print(f'ЧСС: {vpg_analyzer.get_report(self.__vpg, self.__fps)}')

    def start(self):
        self._registrate()
        self._analyzer()