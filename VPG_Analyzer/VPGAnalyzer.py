import numpy as np
from scipy.signal import butter, sosfilt
from numpy.fft import rfft, rfftfreq
from scipy.signal import find_peaks_cwt

from VPG_Analyzer.IVPGAnalyzer import IVPGAnalyzer


class VPGAnalyzer(IVPGAnalyzer):
    def __init__(self):
        self.win_size = 6
        self.lowcut = 0.3
        self.highcut = 2
        self.order = 5

        self.ww1 = 2
        self.ww2 = 15


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
    def smooth(signal: list, n: int) -> np.ndarray:
        """
        Метод сглаживания сигнала
        :param signal:
        :param n:
        :return:
        """
        n_sig = [0] * (n - 1)
        for i in range(n-1, len(signal)):
            n_sig.append(np.mean(signal[i - (n - 1):i+1]))
        return np.array(n_sig)

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

    def filt(self, vpg: list, fd: float) -> np.ndarray:
        """
        Метод фильтрации сигнала ВПГ
        :param vpg: Сигнал
        :param fd: Частота дискретизации
        :return: Отфильтрованный сигнал ВПГ
        """
        vpg = self.butter_bandpass_filter(vpg, self.lowcut, self.highcut, fd, order=self.order)
        vpg = self.smooth(vpg, self.win_size)
        return vpg

    def _adapt_smooth(self, sig: list) -> np.ndarray:
        """
        Метод адаптивной фильтрации
        :param sig: Сигнал
        :return: Отфильтрованный сигнал
        """
        n_sig = np.array(sig)
        for i in range(2, len(sig) - 2):
            diff_r = sig[i + 1] - sig[i]
            diff_l = sig[i] - sig[i - 1]

            if sig[i] > 1.5 * sig[i - 1] or sig[i] > 1.5 * sig[i + 1] or 1.5 * sig[i] < sig[i - 1] or 1.5 * sig[i] < \
                    sig[i + 1]:
                n_sig[i] = (sig[i - 1] + sig[i] + sig[i + 1]) / 3

            if (abs(diff_r) > 1.5 * abs(diff_l) and diff_l * diff_r < 0) or (
                    abs(diff_l) > 1.5 * abs(diff_r) and diff_l * diff_r < 0):
                n_sig[i] = (sig[i - 1] + sig[i] + sig[i + 1]) / 3

        return n_sig

    def _adapt_smooth_rmssd(self, sig: list) -> np.ndarray:
        """
        Метод адаптивной фильтрации для расчёта RMSSD
        :param sig: Сигнал
        :return: Отфильтрованный сигнал
        """
        n_sig = np.array(sig)
        for i in range(1, len(sig) - 1):
            if sig[i] > 2 * sig[i - 1] or sig[i] > 2 * sig[i + 1] or 2 * sig[i] < sig[i - 1] or 2 * sig[i] < sig[i + 1]:
                n_sig[i] = (sig[i - 1] + sig[i + 1]) / 2

            if sig[i] > 2 * sig[i - 1] or sig[i] > 2 * sig[i + 1] or 2 * sig[i] < sig[i - 1] or 2 * sig[i] < sig[i + 1]:
                n_sig[i] = (sig[i - 1] + sig[i] + sig[i + 1]) / 3

        return n_sig

    def find_peaks(self, vpg: list) -> np.ndarray:
        """
        Метод поиска пиков на ВПГ сигнале
        :param vpg: Сигнал ВПГ
        :return: Список индексов элементов, соответствующим пикам
        """
        if len(vpg) == 0:
            return np.array([])
        return find_peaks_cwt(vpg, np.arange(self.ww1, self.ww2))

    def sdann(self, peaks: list, fd: float, f=1) -> float:
        """
        Метод расчёта параметра вариабельности сердечного ритма SDANN
        :param peaks: Индексы эллементов соответствующих пикам
        :param fd: Частота дискретизации
        :param f: Флаг отвечающий за фильтрацию
        :return: Значение SDANN или None, если не возможно рассчитать
        """
        if len(peaks) < 2:
            return None
        peaks = np.diff(peaks)
        if f:
            peaks = self._adapt_smooth(peaks)
        return np.std(peaks) * (1 / fd)

    def rmssd(self, peaks: list, fd: float, f=1) -> float:
        """
        Метод расчёта параметра вариабельности сердечного ритма RMSSD
        :param peaks: Индексы эллементов соответствующих пикам
        :param fd: Частота дискретизации
        :param f: Флаг отвечающий за фильтрацию
        :return: Значение RMSSD или None, если не возможно рассчитать
        """
        if len(peaks) < 2:
            return None
        peaks = np.diff(peaks)
        if f:
            peaks = self._adapt_smooth_rmssd(peaks)
        peaks = np.diff(peaks)
        s = 0
        for i in peaks:
            s += i ** 2
        if len(peaks) == 0:
            return None
        return np.sqrt(s / len(peaks)) * (1 / fd)

    def nn50(self, peaks: list, fd: float) -> tuple:
        """
        Метод расчёта ???????????????????
        :param peaks: Индексы эллементов соответствующих пикам
        :param fd: Частота дискретизации
        :return: ??????????????????
        """
        if len(peaks) < 2:
            return None
        smoothed_peaks = self._adapt_smooth(peaks)
        peaks = np.diff(peaks)
        smoothed_peaks = np.diff(smoothed_peaks)

        n = 0
        sm_n = 0
        for i in range(len(peaks)):
            if peaks[i] * (1 / fd) > 0.050:
                n += 1
            if smoothed_peaks[i] * (1 / fd) > 0.050:
                sm_n += 1

        return n, sm_n

    def get_sdann(self, vpg: list, fd: float, f=1) -> float:
        """
        Метод расчёта SDANN по ВПГ сигналу
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :param f: Флаг для фильтрации
        :return: SDANN
        """
        vpg_peaks = self.find_peaks(vpg)
        return self.sdann(vpg_peaks, fd, f)

    def get_rmssd(self, vpg: list, fd: float, f=1) -> float:
        """
        Метод расчёта RMSSD по ВПГ сигналу
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :param f: Флаг для фильтрации
        :return: RMSSD
        """
        vpg_peaks = self.find_peaks(vpg)
        return self.rmssd(vpg_peaks, fd, f)

    def get_nn50(self, vpg: list, fd: float) -> tuple:
        """
        Метод расчёта NN50 по ВПГ сигналу
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :param f: Флаг для фильтрации
        :return: NN50
        """
        vpg_peaks = self.find_peaks(vpg)
        return self.nn50(vpg_peaks, fd)

    def mean_distance_peaks(self, peaks: list) -> float:
        """
        Расчёт средней дистанции между пиками
        :param peaks: Пики
        :return: Среднее значение дистанции
        """
        if len(peaks) < 2:
            return None
        peaks_diff = np.diff(peaks)
        return float(np.mean(peaks_diff))

    def get_hr_peak(self, vpg: list, fd: float) -> float:
        """
        Метод расчёта ЧСС по ВПГ сигналу при помощи пиков
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :return: hr - ЧСС
        """
        vpg_peaks = self.find_peaks(vpg)
        mean_dist = self.mean_distance_peaks(vpg_peaks)
        if mean_dist is None:
            return None
        if mean_dist == 0:
            return None
        return fd / mean_dist * 60

    def get_hr_spec(self, vpg: list, fd: float) -> float:
        """
        Метод расчёта ЧСС по ВПГ сигналу при помощи спектра
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