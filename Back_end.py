import multiprocessing as mp
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time
import json

from VPGGenerator.VPGGenerator import VPGGenerator
from VPGAnalyzer.VPGAnalyzer import VPGAnalyzer


class App:
    def __init__(self, path='Data'):
        self.__path = path
        self.__queue = mp.Queue()
        self.__frame_handler_process = mp.Process(target=self._frame_handler, args=(self.__queue,))
        self.vpg = []
        self.__vpg_filt = []
        self.frames = []
        self.fps = 0

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

        with open('vpg.json', 'w') as file:
            json.dump(vpg, file)

    def _registrate(self):
        self.__frame_handler_process.start()

        cap = cv2.VideoCapture(0)
        self.fps = cap.get(cv2.CAP_PROP_FPS)

        while (True):
            ret, frame = cap.read()

            # Если кадр не считался выйти из цикла
            if ret == False:
                cap.release()
                cv2.destroyAllWindows()
                break

            cv2.imshow('Video', frame)
            self.__queue.put(frame)
            self.frames.append(frame)

            # Если нажата кнопка закончить регистрацию
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cap.release()
                cv2.destroyAllWindows()
                break

        self.__queue.put(None)
        self.__frame_handler_process.join()

        # Получение сигнала ВПГ
        with open("vpg.json", 'r') as file:
            self.vpg = json.load(file)

    def _analyzer(self):
        vpg_analyzer = VPGAnalyzer()

        # Избавление от кадров без лица
        for i in range(len(self.vpg)):
            if self.vpg[i] is None:
                if i == 0:
                    self.vpg[i] = 0
                else:
                    self.vpg[i] = self.vpg[i - 1]

        # Нормолизуем сигнал
        self.vpg = (self.vpg - np.mean(self.vpg)) / np.std(self.vpg)

        plt.plot(self.vpg)

        # Фильтрация
        self.__vpg_filt = vpg_analyzer.filt(self.vpg, self.fps)

        plt.plot(self.__vpg_filt)
        plt.show()

        # Расчёт ЧСС
        print(f'Длинна сигнала: {len(self.vpg)}')
        print(f'ЧСС: {vpg_analyzer.get_report(self.__vpg_filt, self.fps)}')

    def start(self):
        self._registrate()
        self._analyzer()