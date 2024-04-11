import cv2
import mediapipe as mp
import numpy as np
import onnxruntime as ort
import pandas as pd

from Mimic_Analyzer.IMimicAnalyzer import IMimicAnalyzer


class MimicAnalyzer(IMimicAnalyzer):
    def __init__(self):
        self.onnx_name_au_encoder = 'LibreFace_AU_Encoder.onnx'
        self.ort_session_au_encoder = ort.InferenceSession(self.onnx_name_au_encoder)

        self.onnx_name_au_intensity = 'LibreFace_AU_Intensity.onnx'
        self.ort_session_au_intensity = ort.InferenceSession(self.onnx_name_au_intensity)

        self.onnx_name_au_presence = 'LibreFace_AU_Presence.onnx'
        self.ort_session_au_presence = ort.InferenceSession(self.onnx_name_au_presence)

        self.onnx_name_expression = 'LibreFace_FE.onnx'
        self.ort_session_expression = ort.InferenceSession(self.onnx_name_expression)

        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                refine_landmarks=True,
                max_num_faces=1,
                min_detection_confidence=0.5)

        FACEMESH_LIPS = [(61, 146), (146, 91), (91, 181), (181, 84), (84, 17),
                         (17, 314), (314, 405), (405, 321), (321, 375),
                         (375, 291), (61, 185), (185, 40), (40, 39), (39, 37),
                         (37, 0), (0, 267),
                         (267, 269), (269, 270), (270, 409), (409, 291),
                         (78, 95), (95, 88), (88, 178), (178, 87), (87, 14),
                         (14, 317), (317, 402), (402, 318), (318, 324),
                         (324, 308), (78, 191), (191, 80), (80, 81), (81, 82),
                         (82, 13), (13, 312), (312, 311), (311, 310),
                         (310, 415), (415, 308)]

        FACEMESH_LEFT_EYE = [(263, 249), (249, 390), (390, 373), (373, 374),
                             (374, 380), (380, 381), (381, 382), (382, 362),
                             (263, 466), (466, 388), (388, 387), (387, 386),
                             (386, 385), (385, 384), (384, 398), (398, 362)]

        FACEMESH_RIGHT_EYE = [(33, 7), (7, 163), (163, 144), (144, 145),
                              (145, 153), (153, 154), (154, 155), (155, 133),
                              (33, 246), (246, 161), (161, 160), (160, 159),
                              (159, 158), (158, 157), (157, 173), (173, 133)]

        self.Left_eye = []
        self.Right_eye = []
        self.Lips = []

        for (x, y) in FACEMESH_LEFT_EYE:
            if x not in self.Left_eye:
                self.Left_eye.append(x)
            if y not in self.Left_eye:
                self.Left_eye.append(y)

        for (x, y) in FACEMESH_RIGHT_EYE:
            if x not in self.Right_eye:
                self.Right_eye.append(x)
            if y not in self.Right_eye:
                self.Right_eye.append(y)

        for (x, y) in FACEMESH_LIPS:
            if x not in self.Lips:
                self.Lips.append(x)
            if y not in self.Lips:
                self.Lips.append(y)

    def detect_landmarks(self,
                         image: np.ndarray,
                         draw_mesh: bool = False) -> tuple:
        """
        Метод локализации точек лица

        :param image: Изображение
        :param draw_mesh: Флаг о необходимости отрисовки сетки лица

        :return: Изображение с отрисованной сеткой лица и массив с координатами точек
        """
        # Convert the BGR image to RGB and process it with MediaPipe Face Mesh
        results = self.face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results is None:
            return None, None
        if not results.multi_face_landmarks:
            return None, None

        annotated_image = image.copy()
        face_landmarks = results.multi_face_landmarks[0]

        if draw_mesh:
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_tesselation_style())
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_contours_style())
            self.mp_drawing.draw_landmarks(
                image=annotated_image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_iris_connections_style())

        lm_left_eye_x = []
        lm_left_eye_y = []
        lm_right_eye_x = []
        lm_right_eye_y = []
        lm_lips_x = []
        lm_lips_y = []
        for i in self.Left_eye:
            lm_left_eye_x.append(face_landmarks.landmark[i].x)
            lm_left_eye_y.append(face_landmarks.landmark[i].y)
        for i in self.Right_eye:
            lm_right_eye_x.append(face_landmarks.landmark[i].x)
            lm_right_eye_y.append(face_landmarks.landmark[i].y)
        for i in self.Lips:
            lm_lips_x.append(face_landmarks.landmark[i].x)
            lm_lips_y.append(face_landmarks.landmark[i].y)
        lm_x = lm_left_eye_x + lm_right_eye_x + lm_lips_x
        lm_y = lm_left_eye_y + lm_right_eye_y + lm_lips_y
        landmark = np.array([lm_x, lm_y]).T

        return annotated_image, landmark

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        """
        Метод упорядочивания координат углов четырехугольника,
        по которым будет вырезаться и выравниваться прямоугольник лица

        :param pts: Координаты вершин четырехугольника

        :return: Упорядоченные координаты вершин четырехугольника
        """
        # Initialize a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype='float32')
        # The top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        # Now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        # Return the ordered coordinates
        return rect

    @staticmethod
    def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Метод вырезания выравненного прямоугольника лица по координатам 4 точек

        :param image: Изображение
        :param pts: Упорядоченные координаты вершин четырехугольника

        :return: Выравненное изображение лица
        """
        # Obtain a consistent order of the points and
        # unpack them individually
        rect = MimicAnalyzer.order_points(pts)
        (tl, tr, br, bl) = rect
        # Compute the width of the new image, which will be the
        # maximum distance between bottom-right and bottom-left
        # x-coordiates or the top-right and top-left x-coordinates
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        # Compute the height of the new image, which will be the
        # maximum distance between the top-right and bottom-right
        # y-coordinates or the top-left and bottom-left y-coordinates
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        # Now that we have the dimensions of the new image, construct
        # the set of destination points to obtain a 'birds eye view',
        # (i.e. top-down view) of the image, again specifying points
        # in the top-left, top-right, bottom-right, and bottom-left order
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype='float32')
        # Compute the perspective transform matrix and then apply it
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        # Return the warped image
        return warped

    @staticmethod
    def image_align(img: np.ndarray,
                    face_landmarks: np.ndarray,
                    output_size: int = 256,
                    enable_padding: bool = True,
                    x_scale: float = 1.,
                    y_scale: float = 1.,
                    em_scale: float = 0.1,
                    pad_mode: str = 'const') -> np.ndarray:
        """
        Метод выравнивания и формирования изображения лица,
        удовлетворяющего требованиям нейросетевых моделей

        :param img: Изображение
        :param face_landmarks: Координаты точек лица
        :param output_size: Размер стороны квадрата выходного изображения лица
        :param enable_padding: Флаг необходимости использования отступов
        :param x_scale: Коэффициент масштабирования
        :param y_scale: Коэффициент масштабирования
        :param em_scale: Коэффициент масштабирования
        :param pad_mode: Режим добавления отступов

        :return: Выравненное изображение лица
        """
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        lm = face_landmarks
        lm[:, 0] *= img.shape[1]
        lm[:, 1] *= img.shape[0]

        lm_eye_right = lm[0:16]
        lm_eye_left = lm[16:32]
        lm_mouth_outer = lm[32:]

        lm_mouth_outer_x = lm_mouth_outer[:, 0].tolist()
        left_index = lm_mouth_outer_x.index(min(lm_mouth_outer_x))
        right_index = lm_mouth_outer_x.index(max(lm_mouth_outer_x))

        # Calculate auxiliary vectors
        eye_left = np.mean(lm_eye_left, axis=0)
        eye_right = np.mean(lm_eye_right, axis=0)
        eye_avg = (eye_left + eye_right) * 0.5
        eye_to_eye = eye_right - eye_left
        mouth_avg = (lm_mouth_outer[left_index, :] + lm_mouth_outer[right_index, :]) / 2.0
        eye_to_mouth = mouth_avg - eye_avg

        # Choose oriented crop rectangle
        x = eye_to_eye - np.flipud(eye_to_mouth) * [-1, 1]
        x /= np.hypot(*x)
        x *= max(np.hypot(*eye_to_eye) * 2.0, np.hypot(*eye_to_mouth) * 1.8)
        x *= x_scale
        y = np.flipud(x) * [-y_scale, y_scale]
        c = eye_avg + eye_to_mouth * em_scale
        quad = np.stack([c - x - y, c - x + y, c + x + y, c + x - y])
        qsize = np.hypot(*x) * 2

        # Shrink
        shrink = int(np.floor(qsize / output_size * 0.5))
        if shrink > 1:
            rsize = (int(np.rint(float(img.shape[1]) / shrink)), int(np.rint(float(img.shape[0]) / shrink)))
            img = cv2.resize(img, rsize)
            quad /= shrink
            qsize /= shrink

        # Crop
        border = max(int(np.rint(qsize * 0.1)), 3)
        crop = (int(np.floor(min(quad[:, 0]))), int(np.floor(min(quad[:, 1]))),
                int(np.ceil(max(quad[:, 0]))), int(np.ceil(max(quad[:, 1]))))
        crop = (max(crop[0] - border, 0), max(crop[1] - border, 0),
                min(crop[2] + border, img.shape[1]), min(crop[3] + border, img.shape[0]))

        if crop[2] - crop[0] < img.shape[1] or crop[3] - crop[1] < img.shape[0]:
            img = img[crop[1]:crop[3], crop[0]:crop[2]]
            quad -= crop[0:2]

        # Pad
        pad = (int(np.floor(min(quad[:, 0]))), int(np.floor(min(quad[:, 1]))),
               int(np.ceil(max(quad[:, 0]))), int(np.ceil(max(quad[:, 1]))))
        pad = (max(-pad[0] + border, 0), max(-pad[1] + border, 0),
               max(pad[2] - img.shape[1] + border, 0), max(pad[3] - img.shape[0] + border, 0))

        if enable_padding and max(pad) > border - 4:
            pad = np.maximum(pad, int(np.rint(qsize * 0.3)))
            if pad_mode == 'const':
                img = np.pad(np.float32(img), ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)),
                             'constant', constant_values=0)
            else:
                img = np.pad(np.float32(img), ((pad[1], pad[3]), (pad[0], pad[2]), (0, 0)), 'reflect')
            h, w, _ = img.shape
            y, x, _ = np.ogrid[:h, :w, :1]
            mask = np.maximum(1.0 - np.minimum(np.float32(x) / pad[0], np.float32(w - 1 - x) / pad[2]),
                              1.0 - np.minimum(np.float32(y) / pad[1], np.float32(h - 1 - y) / pad[3]))
            blur = qsize * 0.02
            # img += (scipy.ndimage.gaussian_filter(img, [blur, blur, 0]) - img) * np.clip(mask * 3.0 + 1.0, 0.0, 1.0)
            # img += (np.median(img, axis=(0, 1)) - img) * np.clip(mask, 0.0, 1.0)
            img = np.uint8(np.clip(np.rint(img), 0, 255))

            quad += pad[:2]

        # Four point transform
        pts = (quad + 0.5).flatten()
        pts = list(zip(pts[0::2], pts[1::2]))
        pts = np.array(pts)
        img = MimicAnalyzer.four_point_transform(img, pts)

        # Resize
        img = cv2.resize(img, (output_size, output_size))

        # Center crop
        crop_size = 224
        w, h, c = img.shape
        th, tw = (crop_size, crop_size)
        i = int(round((h - th) / 2.))
        j = int(round((w - tw) / 2.))
        img = img[i:i + th, j:j + tw, :]

        # Normalize
        def normalize_image(image, mean, std):
            for channel in range(3):
                image[:, :, channel] = (image[:, :, channel] - mean[channel]) / std[channel]
            return image

        img = normalize_image(img / 255.0,
                              mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])

        return img

    def predict(self, aligned_image: np.ndarray) -> dict:
        """
        Метод предсказания значений двигательных единиц и эмоций

        :param aligned_image: Выравненное изображение лица

        :return: Словарь со значениями двигательных единиц и эмоций
        """
        aligned_image = np.transpose(aligned_image, (2, 0, 1))
        aligned_image = np.expand_dims(aligned_image, axis=0)
        aligned_image = np.float32(aligned_image)

        pred = self.ort_session_au_encoder.run(
            None,
            {'image': aligned_image},
        )[0]
        pred = np.squeeze(pred, axis=(2, 3))

        # AU intensity
        pred_au_intensity = self.ort_session_au_intensity.run(
            None,
            {'feature': pred},
        )[0]
        # pred_au_intensity = np.squeeze(pred_au_intensity, axis=0).astype(float).tolist()
        pred_au_intensity = np.squeeze(pred_au_intensity, axis=0).astype(float)
        # pred_au_intensity = np.clip(pred_au_intensity * 5, 0, 5).tolist()
        # pred_au_intensity = np.clip(pred_au_intensity * 5, 0, 1).tolist()
        pred_au_intensity = np.clip(pred_au_intensity * 2, 0, 1).tolist()

        # AU presence
        pred_au_presence = self.ort_session_au_presence.run(
            None,
            {'feature': pred},
        )[0]
        pred_au_presence = np.squeeze(pred_au_presence, axis=0)
        # pred_au_presence = np.clip(pred_au_presence * 5, 0, 1)
        pred_au_presence = (pred_au_presence > 0.5).astype(bool).tolist()

        # expression
        pred_expression = self.ort_session_expression.run(
            None,
            {'image': aligned_image},
        )[0]
        pred_expression = np.squeeze(pred_expression, axis=0).astype(float).tolist()

        # print(pred_expression, flush=True)

        pred_expression_max = np.max(pred_expression)
        # pred_expression_exp = [np.exp(el - pred_expression_max) for el in pred_expression]
        pred_expression_exp = [np.exp(el - pred_expression_max) if el>=0.01 else 0. for el in pred_expression]


        pred_expression_sum = np.sum(pred_expression_exp)
        # pred_expression_normalized = [el / pred_expression_sum for el in pred_expression_exp]
        pred_expression_normalized = [el / pred_expression_sum if el!=0. else 0. for el in pred_expression_exp]

        mimic_results = {}
        mimic_results['pred_au_intensity'] = pred_au_intensity
        mimic_results['pred_au_presence'] = pred_au_presence
        mimic_results['pred_expression'] = pred_expression_normalized
        # mimic_results['pred_expression'] = pred_expression

        return mimic_results

    def process_frame(self, frame: np.ndarray) -> dict:
        """
        Метод обработки одного кадра

        :param frame: Кадр

        :return: Словарь со значениями двигательных единиц и эмоций
        """
        annotated_frame, landmarks = self.detect_landmarks(frame)
        if landmarks is None:
            result = dict()
            result['pred_au_intensity'] = [0] * 12
            result['pred_au_presence'] = [False] * 12
            result['pred_expression'] = [0] * 8
        else:
            aligned_face_image = self.image_align(frame, landmarks)
            result = self.predict(aligned_face_image)

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
        intensity_au_names = ['1', '2', '4', '5', '6', '9', '12', '15', '17', '20', '25', '26']
        intensity_au_values = []
        for result in results:
            intensity_au_values.append(result['pred_au_intensity'])

        presence_au_names = ['1', '2', '4', '6', '7', '10', '12', '14', '15', '17', '23', '24']
        presence_au_values = []
        for result in results:
            presence_au_values.append(result['pred_au_presence'])

        expression_names = ['Neutral', 'Happiness', 'Sadness', 'Surprise',
                            'Fear', 'Disgust', 'Anger', 'Contempt']
        expression_values = []
        for result in results:
            expression_values.append(result['pred_expression'])

        df_au_intensity = pd.DataFrame(intensity_au_values, columns=intensity_au_names)
        df_au_presence = pd.DataFrame(presence_au_values, columns=presence_au_names)
        df_face_expression = pd.DataFrame(expression_values, columns=expression_names)

        return df_au_intensity, df_au_presence, df_face_expression
