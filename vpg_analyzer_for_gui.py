from VPG_Analyzer.VPGAnalyzer import VPGAnalyzer
import numpy as np

def vpg_analyzer(vpg, fps):
    vpg_sample_analyzer = VPGAnalyzer()

    # Избавление от кадров без лица
    for i in range(len(vpg)):
        if vpg[i] is None:
            if i == 0:
                vpg[i] = 0
            else:
                vpg[i] = vpg[i - 1]

    # Нормолизуем сигнал
    vpg = (vpg - np.mean(vpg)) / np.std(vpg)

    # Фильтрация
    vpg_filt = vpg_sample_analyzer.filt(vpg, fps)

    # length of window to hrv estimation
    win_size = int(10 / fps)

    if len(vpg) <= win_size:

        return 0
    
    hrv = {"hr": [None] * (win_size - 1), "sdann": [None] * (win_size - 1), "rmssd": [None] * (win_size - 1), "nn50": [None] * (win_size - 1)}
    
    for i in range(len(vpg) - win_size):

        hrv["hr"].append(vpg_sample_analyzer.get_hr_peak(vpg_filt[i:i+win_size], fps))
        peaks = vpg_sample_analyzer.find_peaks(vpg_filt[i:i+win_size])
        hrv["sdann"].append(vpg_sample_analyzer.sdann(peaks, fps))
        hrv["rmssd"].append(vpg_sample_analyzer.rmssd(peaks, fps))
        hrv["nn50"].append(vpg_sample_analyzer.nn50(peaks, fps))

    print(len(hrv['hr']), len(vpg))

    return hrv

    # Расчёт ЧСС
    print(f'Длинна сигнала: {len(vpg)}')
    print(f'ЧСС: {vpg_sample_analyzer.get_hr_peak(vpg_filt, fps)}')
    peaks = vpg_sample_analyzer.find_peaks(vpg_filt)
    print(f'SDANN: {vpg_sample_analyzer.sdann(peaks, fps)}')
    print(f'RMSSD: {vpg_sample_analyzer.rmssd(peaks, fps)}')
    print(f'NN50: {vpg_sample_analyzer.nn50(peaks, fps)}')