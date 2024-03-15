import time

from Back_end_mimic import App

if __name__ == '__main__':

    start_time = time.time()
    app = App()
    app.start()
    finish_time = time.time()
    print((finish_time - start_time) / 60)
