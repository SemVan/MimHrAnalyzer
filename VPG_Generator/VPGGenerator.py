import numpy as np
import cv2
import dlib

from VPG_Generator.IVPGGenerator import IVPGGenerator


class VPGGenerator(IVPGGenerator):
    def __init__(self, predictor_path='', cascade_path=''):
        """
        :param predictor_path:
        :param cascade_path: Путь к файлу с каскадами хаара
        """
        if len(predictor_path) == 0:
            predictor_path = 'shape_predictor_68_face_landmarks.dat'
        if len(cascade_path) == 0:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml'
        self.__predictor = dlib.shape_predictor(predictor_path)
        self.__cascade = cv2.CascadeClassifier(cascade_path)

    def detect_face(self, frame: np.ndarray) -> tuple:
        """
        Метод выделения лица на изображении при помощи каскадов хаара
        :param frame: Изображение
        :return: (only_face, rectungle) - Кадр с лицом, координаты прямоугольника
        """
        faces = self.__cascade.detectMultiScale(frame,
                                                scaleFactor=1.1,
                                                minNeighbors=5,
                                                minSize=(100, 100),
                                                maxSize=(550, 550))
        # Если есть лицо
        if len(faces) > 0:
            x = faces[0][0]         # Координата x прямоугольника
            y = faces[0][1]         # Координата y прямоугольника
            width = faces[0][2]     # Ширина прямоугольника
            height = faces[0][3]    # Высота прямоугольника

            only_face = frame[y:y + height,
                              x:x + width]

            rectangle = [x, y,
                         x + width - 1, y + height - 1]

            return only_face, np.array(rectangle)

        # Если нет лица
        return frame, np.array([])

    def get_landmarks(self, frame: np.ndarray, rectangle: list) -> np.matrix:
        """
        Метод выделения контрольных точек на лице
        :param frame: Изображение
        :param rectangle: Координаты прямоугольника с лицом
        :return: Массив координат [[x, y], ...]
        """
        rect = dlib.rectangle(0, 0, frame.shape[0], frame.shape[1])
        if len(rectangle) != 0:
            x1, y1, x2, y2 = rectangle
            rect = dlib.rectangle(int(x1), int(y1), int(x2 + 1), int(y2 + 1))
        return np.matrix([[p.x, p.y] for p in self.__predictor(frame, rect).parts()])

    def _get_segmented_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Метод для расчёта одного кадра ВПГ
        :param frame: Кадр
        :return: vpg_frame - Массив
        """
        # Ищем лицо
        face_frame, rectangle = self.detect_face(frame)
        if len(rectangle) == 0:
            return np.array([])

        # Ищем контрольные точки
        frame_gray = cv2.cvtColor(face_frame, cv2.COLOR_BGR2GRAY)
        points = self.get_landmarks(frame_gray, [])

        #Формируем области интереса
        ver = [50, 33, 30, 29]              # Точки на носу
        hor = [4, 5, 6, 7, 8, 9, 10, 11]    # Точки на подбородке

        channels = cv2.split(face_frame)
        channels = np.array(channels, np.float64)
        '''channels[1] = channels[1] / np.max(channels[1])
        channels[0] = channels[0] / np.max(channels[0])
        channels[2] = channels[2] / np.max(channels[2])'''

        one_frame_vpg = np.zeros(shape=(3, len(ver) - 1, len(hor) - 1), dtype=np.float64)
        one_frame_count = 0

        try:
            for i in range(len(hor) - 1):
                hl_x = points[hor[i]][0, 0]
                lr_x = points[hor[i + 1]][0, 0]

                for j in range(len(ver) - 1):
                    hl_y = points[ver[j + 1]][0, 1]
                    lr_y = points[ver[j]][0, 1]

                    if i != 3 or i != 4 and j != 2:
                        submats = np.asarray([x[hl_y:lr_y, hl_x:lr_x] for x in channels])
                        one_frame_count += submats.shape[0] * submats.shape[1]

                        for k in range(len(channels)):
                            one_frame_vpg[k][len(ver) - j - 2][i] = np.sum(submats[k])
        except:
            return np.array([])

        return one_frame_vpg / one_frame_count

    @staticmethod
    def _get_RGB(one_frame_vpg: np.ndarray) -> tuple:
        """
        Метод формирования каналов R G B
        :param one_frame_vpg: - Сигналы в областях интереса
        :return: R, G, B - Сигналы R G B
        """
        return np.sum(one_frame_vpg[2]), np.sum(one_frame_vpg[1]), np.sum(one_frame_vpg[0])

    @staticmethod
    def _vpg_func(r: float, g: float, b: float) -> float:
        """
        Метод преобразования каналов в отсчёт ВПГ
        :param r: Красный канал
        :param g: Зелёный канал
        :param b: Синий канал
        :return: ВПГ
        """
        return - 1 * g / (1 * r - 65 * b)

    def get_vpg_discret(self, frame: np.ndarray) -> float:
        """
        Метод расчёта одного отсчёта ВПГ
        :param frame: Кадр
        :return: отсчёт ВПГ / если нет лица то вернёт None
        """
        try:
            one_frame_vpg = self._get_segmented_frame(frame)
            # Проверка на наличие лица
            if len(one_frame_vpg) != 3:
                return None
            r, g, b = self._get_RGB(one_frame_vpg)
            #r, g, b = self._get_RGB(np.array(cv2.split(frame), np.float64))
        except:
            return None
        return self._vpg_func(r, g, b)

    def get_report(self, frames: list) -> list:
        """
        Метод формирования ВПГ сигнала
        :param frames: Список кадров
        :return: vpg - Сигнал ВПГ (массив значений)
        """
        vpg = []
        for frame in frames:
            value = self.get_vpg_discret(frame)
            vpg.append(value)

        return vpg