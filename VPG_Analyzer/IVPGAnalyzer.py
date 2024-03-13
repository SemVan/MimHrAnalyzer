import numpy as np
from abc import ABC, abstractmethod


class IVPGAnalyzer:
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def filt(self, vpg: list, fd: float) -> list:
        """
        Метод фильтрации сигнала ВПГ
        :param vpg: Сигнал
        :param fd: Частота дискретизации
        :return: Отфильтрованный сигнал ВПГ
        """
        return vpg

    @abstractmethod
    def get_report(self, vpg: list, fd: float) -> float:
        """
        Метод расчёта ЧСС по ВПГ сигналу
        :param vpg: Сигнал ВПГ
        :param fd: Частота дискретизации
        :return: hr - ЧСС
        """
        return 0.0