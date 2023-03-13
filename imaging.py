from queue import Queue, Empty

import matplotlib
import numpy as np
import zmq
from PyQt5.QtCore import Qt, QObject, QThread, QTimer
from PyQt5.QtGui import QImage, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow

context = zmq.Context()
print("Connecting to Flim-Processor…")
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://localhost:5556")
subscriber.setsockopt(zmq.SUBSCRIBE, b"")


class FlimPainter(QObject):
    def __init__(self, queue, image):
        super().__init__()
        self.queue = queue
        self.image = image
        self.maxIntensity = 0
        self.cmap = matplotlib.cm.get_cmap('hot')
        self.intensity_map = np.zeros((256, 256))

    def process(self):
        while True:
            try:
                x, y, intensity = self.queue.get()
                if x > 255 or y > 255:
                    continue

                self.intensity_map[x, y] += intensity

                if self.intensity_map[x, y] > self.maxIntensity:
                    self.maxIntensity = self.intensity_map[x, y]
                cmap_value = self.intensity_map[x, y] / self.maxIntensity
                self.image.setPixel(x, y, QColor.fromRgbF(*self.cmap(cmap_value)[:3]).rgb())
            except Empty:
                pass
            except Exception as e:
                print(e)


class FlimReader(QObject):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue

    def process(self):
        while True:
            message = subscriber.recv()
            message = message.decode('utf-8')
            if message == 'exp':
                continue

            message = message.replace('[', '')
            message = message.replace(']', '')
            message = message.split(',')
            message = [int(i) for i in message]
            x = int(message[2])
            y = int(message[1])
            intensity = int(message[3])
            self.queue.put((x, y, intensity))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.queue = Queue(maxsize=100)
        self.image = QImage(256, 256, QImage.Format_RGB32)
        self.manipulate_pixels()
        self.setGeometry(100, 100, 512, 512)
        self.show()

        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(100)
        self.refresh_timer.timeout.connect(self.update)
        self.refresh_timer.start()

    def manipulate_pixels(self):
        for x in range(256):
            for y in range(256):
                self.image.setPixel(x, y, QColor(0, 0, 0).rgb())

    def paintEvent(self, event):
        qPainter = QPainter(self)
        qPainter.drawImage(0, 0, self.image.scaled(512, 512, Qt.KeepAspectRatio))


if __name__ == '__main__':
    app = QApplication([])

    window = MainWindow()

    reader_thread = QThread()
    reader = FlimReader(queue=window.queue)
    reader.moveToThread(reader_thread)
    reader_thread.started.connect(reader.process)
    reader_thread.start()

    painter_thread = QThread()
    painter = FlimPainter(queue=window.queue, image=window.image)
    painter.moveToThread(painter_thread)
    painter_thread.started.connect(painter.process)
    painter_thread.start()


    app.exec()
