from ctypes import *

import numpy as np
import pandas as pd
from numpy.ctypeslib import ndpointer

from Mimic_Analyzer.IMimicAnalyzer import IMimicAnalyzer


# Ctypes definitions
landmarks_model_num = 68
landmarks2D_size = 2 * landmarks_model_num
landmarks3D_size = 3 * landmarks_model_num
pose_size = 3
aus_intensity_size = 17
aus_presence_size = 18

landmarks2D_array = c_double * landmarks2D_size
landmarks3D_array = c_double * landmarks3D_size
head_pose_array = c_double * pose_size
aus_intensity_array = c_double * aus_intensity_size
aus_presence_array = c_double * aus_presence_size


class FACE_INFO(Structure):
    _fields_ = [("certainty", c_float),
                ("detection_success", c_bool),
                ("landmarks2D", landmarks2D_array),
                ("landmarks3D", landmarks3D_array),
                ("head_rotation", head_pose_array),
                ("head_position", head_pose_array),
                ("aus_intensity", aus_intensity_array),
                ("aus_presence", aus_presence_array)]


# OpenFace caller
class Info3DEstimation(object):
    def __init__(self, openface_shared_lib_path: str):
        self.info3D_model = cdll.LoadLibrary(openface_shared_lib_path)
        self.info3D_model.loadModel()

    def get_3Dinformation(self, image, w, h, calib_matrix, certainty_threshold=0.5):
        calib_matrix_np = np.array(calib_matrix).reshape((9, 1))

        self.info3D_model.trackFaceImageFromArrayDynamic.argtypes = [POINTER(c_ubyte),
                                                                     c_int,
                                                                     c_int,
                                                                     ndpointer(c_double, flags="C_CONTIGUOUS"),
                                                                     POINTER(FACE_INFO)]

        face_info = FACE_INFO(0.0, 0)

        success = self.info3D_model.trackFaceImageFromArrayDynamic(image, w, h, calib_matrix_np, pointer(face_info))
        # print("certainty: ", face_info.certainty)
        # print("success: ", face_info.detection_success)

        if success:
            info3D = dict()

            # # Landmark 2D
            # info3D['landmarks2D'] = np.ndarray(buffer=landmarks2D_array.from_address(addressof(face_info.landmarks2D)),
            #                          shape=(landmarks2D_size,)).reshape((2, landmarks_model_num)).transpose().copy()
            # # Landmarks 3D
            # info3D['landmarks3D'] = np.ndarray(buffer=landmarks3D_array.from_address(addressof(face_info.landmarks3D)),
            #                          shape=(landmarks3D_size,)).reshape((3, landmarks_model_num)).transpose().copy()
            # # Head pose
            # info3D['R'] = np.ndarray(buffer=head_pose_array.from_address(addressof(face_info.head_rotation)),
            #                shape=(pose_size,)).copy()
            # # Head position
            # info3D['T'] = np.ndarray(buffer=head_pose_array.from_address(addressof(face_info.head_position)),
            #                shape=(pose_size,)).copy()

            # AUS intensity
            info3D['AUSint'] = np.ndarray(buffer=aus_intensity_array.from_address(addressof(face_info.aus_intensity)),
                                          shape=(aus_intensity_size,)).copy()

            # AUS presence
            info3D['AUSpres'] = np.ndarray(buffer=aus_presence_array.from_address(addressof(face_info.aus_presence)),
                                           shape=(aus_presence_size,)).copy()

            return success, info3D['AUSint'], info3D['AUSpres']

        else:
            return success, None, None


# Используется scratch-версия knn-классификатора,
# поскольку при использовании метода из sklearn при запуске экзешника, собранного pyinstaller'ом,
# на каждом запуске обработки нового видео появляется на менее чем секунду раздражающее консольное окно.
# При этом никаких сообщений, предупреждений или ошибок нет.
# Победить это удалось, только отказавшись от sklearn
class KNN(object):
    def __init__(self, k):
        self.k = k

    def fit(self, x_train, y_train):
        self.x_train = x_train
        self.y_train = y_train
        self.labels = set(y_train)

    def calculate_euclidean(self, sample1, sample2):
        distance = 0.0
        for i in range(len(sample1)):
            distance += (sample1[i] - sample2[i]) ** 2  # Euclidean Distance = sqrt(sum i to N (x1_i – x2_i)^2)
        return np.sqrt(distance)

    def nearest_neighbors(self, test_sample):
        distances = []  # calculate distances from a test sample to every sample in a training set
        for i in range(len(self.x_train)):
            distances.append((self.y_train[i], self.calculate_euclidean(self.x_train[i], test_sample)))
        distances.sort(key=lambda x: x[1])  # sort in ascending order, based on a distance value
        neighbors = []
        for i in range(self.k):  # get first k samples
            neighbors.append(distances[i][0])
        return neighbors

    def predict(self, test_set):
        predictions = []
        for test_sample in test_set:
            neighbor_labels = self.nearest_neighbors(test_sample)

            prediction = max(neighbor_labels, key=neighbor_labels.count)
            predictions.append(prediction)
        return predictions

    def predict_proba(self, test_set):
        predictions = []
        for test_sample in test_set:
            neighbor_labels = self.nearest_neighbors(test_sample)

            prediction = {}
            for lb in self.labels:
                prediction[lb] = 0

            for lb in neighbor_labels:
                prediction[lb] += 1

            total = sum(prediction.values())
            probability_prediction = {k: v / total for k, v in prediction.items()}

            prob = [probability_prediction[key] for key in sorted(probability_prediction.keys())]
            predictions.append(prob)

        return predictions


class MimicAnalyzer(IMimicAnalyzer):
    def __init__(self):
        self.calib_matrix = [[1.2 * 720.0, 0.0, 360.0],
                             [0.0, 1.2 * 720.0, 288.0],
                             [0.0, 0.0, 1.0]]
        self.meh = Info3DEstimation('./compiled_libraries/OpenFaceDLL.dll')

        self.neigh_model = KNN(5)

        x = pd.read_csv('au_intensities.csv', header=None)
        y = pd.read_csv('targets.csv', header=None).iloc[:, 0]
        x = np.array(x)
        y = np.array(y)

        self.neigh_model.fit(x, y)

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Метод обработки одного кадра

        :param frame: Кадр

        :return: Словарь со значениями двигательных единиц и эмоций
        """
        frame = np.asarray(frame, dtype=np.uint8)

        w = frame.shape[1]
        h = frame.shape[0]

        frame = frame.ctypes.data_as(POINTER(c_ubyte))

        success, pred_au_intensity, pred_au_presence = self.meh.get_3Dinformation(frame, w, h, self.calib_matrix)

        if not success:
            result = dict()
            result['pred_au_intensity'] = [0] * 17
            result['pred_au_presence'] = [False] * 18
            result['pred_expression'] = [0] * 7
        else:
            pred_au_intensity = pred_au_intensity / 5
            pred_au_intensity = pred_au_intensity.astype(float).tolist()

            pred_au_presence = pred_au_presence.astype(bool).tolist()

            pred_expression = self.neigh_model.predict_proba(np.array(pred_au_intensity).reshape(1, -1))
            pred_expression = list(pred_expression[0])

            result = dict()
            result['pred_au_intensity'] = pred_au_intensity
            result['pred_au_presence'] = pred_au_presence
            result['pred_expression'] = pred_expression

        return result

    def get_report(self, frames: list) -> list:
        """
        Метод обработки последовательности кадров

        :param frames: Список кадров

        :return: Список словарей со значениями двигательных единиц и эмоций
        """
        results = []
        for frame in frames:
            result = self.process_frame(frame)
            results.append(result)

        return results

    @staticmethod
    def convert_results_to_dataframes(results: list) -> tuple:
        """
        Метод конвертации значений предсказаний из списка в датафреймы

        :param results: Список словарей со значениями двигательных единиц и эмоций

        :return: Датафреймы со значениями интенсивностей двигательных единиц (df_au_intensity),
        наличием двигательных единиц (df_au_presence) и вероятностями эмоций (df_face_expression)
        """
        intensity_au_names = ['1', '2', '4', '5', '6', '7', '9', '10', '12',
                              '14', '15', '17', '20', '23', '25', '26', '45']
        intensity_au_values = []
        for result in results:
            intensity_au_values.append(result['pred_au_intensity'])

        presence_au_names = ['1', '2', '4', '5', '6', '7', '9', '10', '12',
                             '14', '15', '17', '20', '23', '25', '26', '28', '45']
        presence_au_values = []
        for result in results:
            presence_au_values.append(result['pred_au_presence'])

        expression_names = ['Neutral', 'Happiness', 'Sadness', 'Surprise', 'Fear', 'Disgust', 'Anger']
        expression_values = []
        for result in results:
            expression_values.append(result['pred_expression'])

        df_au_intensity = pd.DataFrame(intensity_au_values, columns=intensity_au_names)
        df_au_presence = pd.DataFrame(presence_au_values, columns=presence_au_names)
        df_face_expression = pd.DataFrame(expression_values, columns=expression_names)

        return df_au_intensity, df_au_presence, df_face_expression
