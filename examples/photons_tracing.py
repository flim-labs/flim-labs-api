import matplotlib
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numpy import linspace

matplotlib.use('Qt5Agg')

from PyQt5.QtCore import QTimer, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

from flim_labs_api import FlimLabsApi

SLICE_SECONDS = 10_000


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setGeometry(512, 512, 1024, 1024)
        self.setWindowTitle('Photons tracing')

        self.api = FlimLabsApi()
        self.api.set_consumer_handler(self.receive_data)

        self.chart = MplCanvas(self, width=12, height=5, dpi=100)
        self.setCentralWidget(self.chart)

        self.slice = 1 * SLICE_SECONDS
        self.channels = [1]
        self.acquisition_time_in_seconds = 60

        self.data = []
        for _ in self.channels:
            self.data.append([])

        # create timer to refresh histogram
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_histogram)
        self.refresh_timer.setInterval(1)
        self.refresh_timer.start()

        # draw a button to start the acquisition
        self.start_button = QPushButton('Start', self)
        self.start_button.move(5, 5)
        self.start_button.clicked.connect(self.start_acquisition)

        self.mutex = QMutex()

        # create a label to show the current phase
        self.phase_label = QLabel(self)
        self.phase_label.move(5, 40)
        self.phase_label.setText('Row received: 0')
        self.phase_label.adjustSize()
        self.rows_received = 0

        # self.data = np.load('correlation_data.npz')['data']

        self.show()

    def closeEvent(self, event):
        self.api.stop_acquisition()
        np.savez_compressed('photons_tracing', data=self.data)
        event.accept()

    def start_acquisition(self):
        self.start_button.setEnabled(False)
        self.api.set_firmware("firmwares\\photons_tracing.flim")
        self.api.acquire_photons_tracing(channels=self.channels,
                                         acquisition_time_seconds=self.acquisition_time_in_seconds)

    def receive_data(self, row_data):
        self.mutex.lock()
        for i, channel in enumerate(self.channels):
            # self.data[i].append(row_data[i] + self.data[i][-1] if len(self.data[i]) > 0 else 0)
            self.data[i].append(row_data[i])
        self.rows_received += 1
        self.mutex.unlock()

    def refresh_histogram(self):
        try:
            self.chart.axes.clear()
            total_x = len(self.data[0])
            slice_x = min(total_x, self.slice)
            if slice_x == 0:
                return
            starting_seconds = max((total_x - slice_x) / SLICE_SECONDS, 0)
            x_data = linspace(starting_seconds, starting_seconds + (self.slice / SLICE_SECONDS),
                              num=min(slice_x, self.slice))
            for i, channel in enumerate(self.channels):
                self.chart.axes.plot(x_data, self.data[i][-slice_x:])
            self.chart.axes.set_xbound(lower=starting_seconds,
                                       upper=starting_seconds + (min(slice_x, self.slice) / SLICE_SECONDS))
            self.chart.axes.set_xlabel('Time Bins (100μs)')
            self.chart.axes.set_ylabel('Photon counts')
            self.chart.draw()
            self.phase_label.setText(f'Bins received: {self.rows_received}')
            self.phase_label.adjustSize()
        except Exception as e:
            print(e)
            import traceback
            traceback.print_exc()
            raise e


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    exit(app.exec())
