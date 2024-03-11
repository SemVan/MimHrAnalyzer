import os
import numpy as np
import matplotlib.pyplot as plt

from VPG_Analyzer.VPGAnalyzer import VPGAnalyzer


PATH_DATA = 'Data'
FPS = 30


def test():
    for file_name in os.listdir(PATH_DATA):
        file_path = os.path.join(PATH_DATA, file_name)
        print(file_name)

        vpg_analyzer = VPGAnalyzer()

        vpg = np.load(file_path, allow_pickle=True)[30:]
        t = np.array(list(range(len(vpg)))) * (1 / FPS)
        vpg = (vpg - np.mean(vpg)) / np.std(vpg)
        plt.plot(t, vpg)

        #print(len(vpg))
        vpg1 = vpg_analyzer.butter_bandpass_filter(vpg, 0.3, 2, FPS, order=5)
        #print(len(vpg))
        win_size = 6
        vpg1 = vpg_analyzer.smooth(vpg1, win_size)
        #print(len(vpg))
        plt.plot(t, vpg1)
        plt.show()

        f, spec = vpg_analyzer.get_spec(vpg1, FPS)
        plt.plot(f, np.abs(spec))
        plt.show()

        print(f'ЧСС: {vpg_analyzer.get_report(vpg, FPS)}')

if __name__ == '__main__':
    test()