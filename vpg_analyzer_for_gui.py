from VPG_Analyzer.VPGAnalyzer import VPGAnalyzer
import numpy as np
import json

def vpg_analyzer(vpg, fps, path):
    vpg_analyzer = VPGAnalyzer()

    face_flags = []
    # Избавление от кадров без лица
    for i in range(len(vpg)):
        if vpg[i] is None:
            if i == 0:
                vpg[i] = 0
            else:
                vpg[i] = vpg[i - 1]
            face_flags.append(False)
        else:
            face_flags.append(True)

    # Нормолизуем сигнал
    vpg = (vpg - np.mean(vpg)) / np.std(vpg)

    # Фильтрация
    vpg_filt = vpg_analyzer.filt(vpg, fps)

    # Расчёт ЧСС
    hr = vpg_analyzer.get_report_hr(vpg_filt, fps)

    # Расчёт SDANN RMSSD NN50
    peaks = vpg_analyzer.find_peaks(vpg_filt)

    hrv = vpg_analyzer.get_report_hrv(vpg_filt, fps, 100)
    hrv['hr'] = hr
    hrv['face'] = face_flags

    with open(path, 'w') as file:
        json.dump(hrv, file)

    return hrv