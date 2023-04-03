import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numpy import linspace

matplotlib.use('Qt5Agg')

import numpy as np
from PyQt5.QtCore import QTimer, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

from flim_labs_api import FlimLabsApi


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.laser_mhz = 40
        self.acquisition_time_in_seconds = 28

        self.x_data = linspace(0, 1000 / self.laser_mhz, 256)
        self.y_data = np.zeros(256)

        self.setGeometry(512, 512, 1024, 1024)
        self.setWindowTitle('Spectroscopy ' + str(self.laser_mhz) + ' MHz')

        self.api = FlimLabsApi()
        self.api.set_consumer_handler(self.receive_point)

        self.chart = MplCanvas(self, width=12, height=5, dpi=100)
        self.chart.axes.plot(self.x_data, self.y_data)
        self.setCentralWidget(self.chart)

        # create timer to refresh histogram
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_histogram)
        self.refresh_timer.setInterval(100)
        self.refresh_timer.start()

        # draw a button to start the acquisition
        self.start_button = QPushButton('Start', self)
        self.start_button.move(5, 5)
        self.start_button.clicked.connect(self.start_acquisition)
        
        # draw a button to STOP the acquisition
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.move(120, 5)
        self.stop_button.clicked.connect(self.stop_acquisition)

        self.mutex = QMutex()

        # create a label to show the current phase
        self.phase_label = QLabel(self)
        self.phase_label.move(5, 40)
        self.phase_label.setText('Points received: 0')
        self.phase_label.adjustSize()
        self.points_received = 0
        
        # create a label to show the time of the acquisition
        self.time_label = QLabel(self)
        self.time_label.move(120, 40)
        self.time_label.setText('Acquisition time: 0')
        self.time_label.adjustSize()
        self.counts = 0

        self.show()

    def closeEvent(self, event):
        np.savez_compressed('spectroscopy', self.x_data, self.y_data)
        self.api.stop_acquisition()
        event.accept()

    def start_acquisition(self):
        self.start_button.setEnabled(False)
        #self.api.set_firmware("firmwares\\spectroscopy_simulator_" + str(self.laser_mhz) + "MHz.flim")
        self.api.set_firmware("firmwares\\spectroscopy_40MHz_lvds_ch1.flim")
        #self.api.set_firmware("firmwares\\spectroscopy_80MHz.flim")
        self.api.acquire_spectroscopy(
            laser_frequency_mhz=self.laser_mhz,
            acquisition_time_seconds=self.acquisition_time_in_seconds
        )
        self.stop_button.setEnabled(True)
        
    def stop_acquisition(self):
        self.stop_button.setEnabled(False)
        self.api.stop_acquisition()
        self.y_data = np.zeros(256)
        self.start_button.setEnabled(True)
             

    def receive_point(self, channel, time_bin, micro_time, monotonic_counter, macro_time):
        self.mutex.lock()
        self.y_data[time_bin] += 1
        self.points_received += 1
        self.mutex.unlock()

    def refresh_histogram(self):
        self.chart.axes.clear()
        self.chart.axes.plot(self.x_data, self.y_data)
        self.chart.axes.set_xlabel('Time (ns)')
        self.chart.axes.set_ylabel('Photon counts')
        self.chart.axes.set_xbound(0, 1000 / self.laser_mhz)
        self.chart.draw()
        # format points received with commas
        self.phase_label.setText(f'Total photons: {self.points_received:,}')
        self.phase_label.adjustSize()
        
        for i in range(self.acquisition_time_in_seconds):
            self.time_label.setText(f'Acquisition time: {str(i)}')
        
        self.time_label.adjustSize()


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    exit(app.exec())
