import json
import os

import cv2

from Frame_handler.FrameHandlerMimic import FrameHandlerMimic
from Mimic_Analyzer.MimicAnalyzer import MimicAnalyzer


class App:
    def __init__(self, path='Data'):
        self.__path = path
        self.__frame_handler = FrameHandlerMimic('mimic.json')
        self.results = []
        self.fps = 0

    @staticmethod
    def _frame_handler(queue) -> None:
        """
        Метод параллельной обработки кадров

        :param queue: Очередь, в которую будут складываться кадры
        """
        mimic_analyzer = MimicAnalyzer()
        results = []

        while True:
            # Если в очереди нет кадров, продолжить ожидать
            if queue.empty():
                continue

            frame = queue.get()

            # Проверка на конец регистрации
            if frame is None:
                break

            result = mimic_analyzer.process_frame(frame)
            results.append(result)

        with open('mimic.json', 'w') as file:
            json.dump(results, file)

    def _registrate(self) -> None:
        """
        Метод регистрации кадров и добавления их в очередь на обработку
        """
        # Запуск процесса обработки
        self.__frame_handler.start()

        cap = cv2.VideoCapture(0)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        path = os.path.join(self.__path, "video.avi")
        video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                self.fps, (frame_width, frame_height))

        while True:
            ret, frame = cap.read()

            # Если кадр не считался, выйти из цикла
            if ret is False:
                cap.release()
                cv2.destroyAllWindows()
                break

            cv2.imshow('Video', frame)
            # Отправка кадра на обработку
            self.__frame_handler.push(frame)
            video.write(frame)

            # Если нажат пробел, закончить регистрацию
            if cv2.waitKey(1) & 0xFF == ord(' '):
                cap.release()
                cv2.destroyAllWindows()
                break

        # Завершение регистрации
        self.__frame_handler.finish()
        # Получение результатов распознавания мимики (С ожиданием обработки)
        self.results = self.__frame_handler.join()

    def _analyzer(self) -> None:
        """
        Метод анализа результатов распознавания двигательных единиц и эмоций
        """
        df_au_intensity, df_au_presence, df_face_expression = MimicAnalyzer.convert_results_to_dataframes(self.results)

        print('Обработано кадров:', len(df_face_expression))

    def start(self) -> None:
        """
        Запуск регистрации кадров, их обработки и анализа результатов распознавания
        """
        self._registrate()
        self._analyzer()
