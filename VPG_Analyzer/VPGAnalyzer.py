import numpy as np
from scipy.signal import butter, sosfilt
from numpy.fft import rfft, rfftfreq

from VPG_Analyzer.IVPGAnalyzer import IVPGAnalyzer


class VPGAnalyzer(IVPGAnalyzer):
    def __init__(self):
        self.win_size = 6
        self.lowcut = 0.3
        self.highcut = 2
        self.order = 5


    @staticmethod
    def butter_bandpass_filter(signal, lowcut, highcut, fd, order=1) -> np.ndarray:
        """
        Метод фильтрации сигнала
        :param signal: Сигнал
        :param lowcut: Частота среза 1
        :param highcut: Частота среза 2
        :param fd: Частота дискретизации
        :param order: Порядок фильтра
        :return: Отфильтрованный сигнал
        """
        sos = butter(order, (lowcut, highcut), 'bp', fs=fd, output='sos')
        return sosfilt(sos, signal)

    @staticmethod
    def smooth(sig, n):
        """
        Метод сглаживания сигнала
        :param sig:
        :param n:
        :return:
        """
        n_sig = [0] * (n - 1)
        for i in range(n-1, len(sig)):
            n_sig.append(np.mean(sig[i - (n - 1):i+1]))
        return n_sig

    @staticmethod
    def get_spec(sig, fd):
        """
        Метод создания спектра сигнала
        :param sig: Сигнал
        :param fd: Частота дискретизации
        :return: Частоты, Спектр
        """
        yf = rfft(sig)
        xf = rfftfreq(len(sig), 1 / fd)
        return xf, yf

    def filt(self, vpg: list, fd: float):
        """
        Метод фильтрации сигнала ВПГ
        :param vpg: Сигнал
        :param fd: Частота дискретизации
        :return: Отфильтрованный сигнал ВПГ
        """
        vpg = self.butter_bandpass_filter(vpg, self.lowcut, self.highcut, fd, order=self.order)
        vpg = self.smooth(vpg, self.win_size)
        return vpg

    def get_report(self, vpg: list, fd: float) -> float:
        """
        Метод расчёта ЧСС по ВПГ сигналу
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :return: hr - ЧСС
        """
        # Переход в частотную область
        f, vpg_spec = self.get_spec(vpg, fd)
        vpg_spec = np.abs(vpg_spec)

        # Расчёт ЧСС
        hr = f[np.argmax(vpg_spec)] * 60
        return hr