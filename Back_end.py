import os

import cv2
import matplotlib.pyplot as plt
import numpy as np

from Frame_handler.FrameHandlerVPG import FrameHandlerVPG
from VPG_Analyzer.VPGAnalyzer import VPGAnalyzer


class App:
    def __init__(self, path='Data'):
        self.__path = path
        self.__frame_handler = FrameHandlerVPG('vpg.json')
        self.vpg = []
        self.__vpg_filt = []
        self.fps = 0

    def _registrate(self):
        """
        Метод регистрации видео
        :return: None
        """
        # Запуск процесса обработки
        self.__frame_handler.start()

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # auto mode
        #cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # manual mode
        #cap.set(cv2.CAP_PROP_EXPOSURE, -5) # примерно 0.0333 мс
        self.fps = cap.get(cv2.CAP_PROP_FPS)

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        path = os.path.join(self.__path, "video.avi")
        video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), self.fps, (frame_width, frame_height))

        while (True):
            #start = time.time()
            ret, frame = cap.read()

            # Если кадр не считался выйти из цикла
            if ret == False:
                cap.release()
                cv2.destroyAllWindows()
                break

            cv2.imshow('Video', frame)
            # Отправка кадра на обработку
            self.__frame_handler.push(frame)
            video.write(frame)
            #print(cap.get(cv2.CAP_PROP_AUTO_EXPOSURE))

            # Если нажата кнопка закончить регистрацию
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cap.release()
                video.release()
                cv2.destroyAllWindows()
                break
            #print(time.time() - start)

        # Завершение регистрации
        self.__frame_handler.finish()
        # Получение сигнала ВПГ (С ожиданием обработки)
        self.vpg = self.__frame_handler.join()

    def _analyzer(self):
        """
        Метод постобработки
        :return: None
        """
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

        plt.plot(self.vpg, label='ВПГ после нормализации')

        # Фильтрация
        self.__vpg_filt = vpg_analyzer.filt(self.vpg, self.fps)

        plt.plot(self.__vpg_filt, label='ВПГ фильтрованный')
        plt.grid()
        plt.legend()
        path = os.path.join(self.__path, "vpg.png")
        plt.savefig(path, dpi=512)
        plt.show()

        # Расчёт ЧСС
        ans = vpg_analyzer.get_report_hr(self.__vpg_filt, self.fps)
        #print(f'Длинна сигнала: {len(self.vpg)}')
        #print(f'Длинна сигнала ЧСС: {len(ans["hr"])}')
        #print(f'ЧСС: {vpg_analyzer.get_hr_peak(self.__vpg_filt, self.fps)}')
        print('Сигнал уникальных ЧСС')
        print(ans["hr_hist"])
        fig, ax = plt.subplots(ncols=2)
        ax[0].plot(ans["hr"])
        ax[1].plot(ans["hr_hist"])
        plt.show()

        # Расчёт SDANN RMSSD NN50
        peaks = vpg_analyzer.find_peaks(self.__vpg_filt)
        print(f'SDANN: {vpg_analyzer.sdann(peaks, self.fps)}')
        print(f'RMSSD: {vpg_analyzer.rmssd(peaks, self.fps)}')
        print(f'NN50: {vpg_analyzer.nn50(peaks, self.fps)}')

    def start(self):
        self._registrate()
        self._analyzer()