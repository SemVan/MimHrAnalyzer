import cv2
import os
import numpy as np
import time
import matplotlib.pyplot as plt

from VPG_Generator.VPGGenerator import VPGGenerator


PATH_DATA = 'Data'


def file_reader(file_path: str, visualize=True) -> tuple:
    """
    Функция прочтения видео
    :param file_path: Путь к файлу
    :param visualize: Проиграть видео или нет
    :return: (frames, fps) - Массив кадров и фпс
    """
    # Инициализируем необходимые переменные
    frames = []

    # Считываем файл
    cap = cv2.VideoCapture(file_path)
    print(int(cap.get(3)), int(cap.get(4)))
    fps = cap.get(cv2.CAP_PROP_FPS)
    while (True):
        ret, frame = cap.read()

        # Если файл закончился выйти из цикла
        if ret == False:
            cap.release()
            if visualize:
                cv2.destroyAllWindows()
            break

        # Если нажата кнопка перестать показывать видео
        if visualize:
            cv2.imshow('Video', frame)
            if cv2.waitKey(int(1000 / fps)) & 0xFF == ord(' '):
                visualize = False
        else:
            cv2.destroyAllWindows()

        #Добавляем frame
        frames.append(frame)

    return np.array(frames), float(fps)


def test_face_detector(vpg_generator, frames: list):
    """
    Метод тестирования выделения лица на изображении
    :param vpg_generator - Объект, который тестируем
    :param frames: - Список кадров
    :return: None
    """
    start = time.time()
    for frame in frames:
        frame, _ = vpg_generator.detect_face(frame)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            cv2.destroyAllWindows()
            break
    print(f'Время test_face_detector: {time.time() - start}')


def test_get_landmarks(vpg_generator, frames: list):
    """
    Метод тестирования выделения контрольных точек на лице
    :param vpg_generator - Объект, который тестируем
    :param frames: - Список кадров
    :return: None
    """

    frame_width = 640
    frame_height = 480
    path = os.path.join("video.avi")
    video = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))
    p = [4, 5, 6, 7, 8, 9, 10, 11, 50, 33, 30, 29]
    graph = dict()
    for i in p:
        graph[i] = [[],[]]

    start = time.time()
    for frame in frames:
        frame = cv2.GaussianBlur(frame, (3, 3), 5)
        frame = cv2.medianBlur(frame, 3)

        face_frame, rectangle = vpg_generator.detect_face(frame)
        points = vpg_generator.get_landmarks(frame, rectangle)

        for i, point in enumerate(np.array(points)[p]):
            #point[0] += rectangle[0]
            #point[1] += rectangle[1]
            graph[p[i]][0].append(point[0])
            graph[p[i]][1].append(point[1])
            frame = cv2.circle(frame, point,
                               radius=2,
                               color=(0, 255, 0),
                               thickness=-1)
            frame = cv2.putText(frame, str(i), point, cv2.FONT_HERSHEY_SIMPLEX ,
                                0.5, (255, 0, 0), 1, cv2.LINE_AA)

        cv2.imshow('Video', frame)
        video.write(frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):
            video.release()
            cv2.destroyAllWindows()
            break

    xx = []
    for k in graph.keys():
        x = np.array(graph[k][0])
        x -= x[0]
        plt.plot(x, label=str(k))
        xx.append(x)
    xx = np.array(xx)
    print(xx.shape)
    plt.legend()
    plt.show()

    mx = []
    for i in range(len(xx[0])):
        mx.append(np.mean(xx[:, i]))
    plt.plot(mx)
    plt.show()

    yy = []
    for k in graph.keys():
        y = np.array(graph[k][1])
        y -= y[0]
        plt.plot(y, label=str(k))
        yy.append(y)
    yy = np.array(yy)
    print(yy.shape)
    plt.legend()
    plt.show()

    my = []
    for i in range(len(yy[0])):
        my.append(np.mean(yy[:, i]))
    plt.plot(my)
    plt.show()

    vpg = vpg_generator.get_report(frames)
    vpg = np.array(vpg)
    vpg = (vpg - np.mean(vpg)) / np.std(vpg)
    plt.plot(vpg, label='ВПГ')

    mx = np.array(mx)
    mx = (mx - np.mean(mx)) / np.std(mx)
    plt.plot(mx, label='кадры')
    plt.legend()
    plt.show()
    np.save("vpg.npy", vpg)
    np.save("mx.npy", mx)

    vpg = vpg_generator.get_report(frames)
    vpg = np.array(vpg)
    vpg = (vpg - np.mean(vpg)) / np.std(vpg)
    plt.plot(vpg, label='ВПГ')

    my = np.array(my)
    my = (my - np.mean(my)) / np.std(my)
    plt.plot(my, label='кадры')
    plt.legend()
    plt.show()
    np.save("my.npy", my)

    '''for i in range(len(graph)):
        x = np.array(graph[p[i]][1])
        x -= x[0]
        plt.plot(x, label=str(p[i]))
    plt.legend()
    plt.show()'''
    #video.release()
    print(f'Время test_get_landmarks: {time.time() - start}')


def test_get_segmented_frame(vpg_generator, frames: list):
    """
    Метод тестирования ...
    :param vpg_generator - Объект, который тестируем
    :param frames: - Список кадров
    :return: None
    """
    start = time.time()
    for frame in frames:
        vpg_frame = vpg_generator._get_segmented_frame(frame)
        vpg_frame = np.mean(vpg_frame[1]) / (np.mean(vpg_frame[0]) + np.mean(vpg_frame[2]))
        print(vpg_frame)
    print(f'Время test_get_segmented_frame: {time.time() - start}')


def test_get_report(vpg_generator, frames: list):
    """
    Метод тестирования генерации ВПГ
    :param vpg_generator - Объект, который тестируем
    :param frames: - Список кадров
    :return: vpg - Сигнал ВПГ
    """
    start = time.time()
    vpg = vpg_generator.get_report(frames)
    print(f'Время test_get_report: {time.time() - start}')
    plt.plot(vpg)
    plt.show()

    return vpg


def test(vpg_generator):
    for file_name in os.listdir('Data'):
        file_path = os.path.join(PATH_DATA, file_name)

        frames, fps = file_reader(file_path, visualize=False)
        print(f'fps: {fps}')
        print(f'Колличество кадров: {len(frames)}')
        print(f'Длительность: {len(frames) / fps}')
        print()
#########################################################################################################
        #Тестируем методы
        print('Тестирование:')
        #test_face_detector(vpg_generator, frames)
        test_get_landmarks(vpg_generator, frames)
        #test_get_segmented_frame(vpg_generator, frames)
        #vpg = test_get_report(vpg_generator, frames)

        #print(frames[0])
        #vpg_generator.get_vpg_discret(frames[54])

        #file_path = file_path.split('.')[0] + '.npy'
        #np.save(file_path, vpg)


if __name__ == '__main__':
    vpg_generator = VPGGenerator()
    test(vpg_generator)