import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numpy import linspace

matplotlib.use('Qt5Agg')

import numpy as np
from PyQt5.QtCore import QTimer, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QSpinBox, QFileDialog, QSplitter, QWidget, QVBoxLayout, QHBoxLayout

from flim_labs_api import FlimLabsApi


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.laser_mhz = 80
        self.acquisition_time_in_seconds = 10
        self.output_filename = 'spectroscopy.bin'
        self.output_filename_1 = 'spectroscopy.csv'

        self.x_data = np.zeros(256)
        self.y_data = np.zeros(256)

        self.setGeometry(512, 512, 1024, 1024)
        

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
                
        
        # create a label and spin box for acquisition time setting
        self.time_label = QLabel('Acquisition Time (Seconds):', self)
        self.time_label.move(375, 5)
        self.time_label.adjustSize()

        self.time_spinbox = QSpinBox(self)
        self.time_spinbox.move(550, 5)
        self.time_spinbox.setMinimum(1)
        self.time_spinbox.setMaximum(300)
        self.time_spinbox.setValue(self.acquisition_time_in_seconds)
        self.time_spinbox.valueChanged.connect(self.set_acquisition_time)
        
        # create a label and spin box for laser frequency setting 
        self.time_label = QLabel('Laser frequency(MHz):', self)
        self.time_label.move(725, 5)
        self.time_label.adjustSize()

        self.time_spinbox = QSpinBox(self)
        self.time_spinbox.move(900, 5)
        self.time_spinbox.setMinimum(20)
        self.time_spinbox.setMaximum(80)
        self.time_spinbox.setValue(self.laser_mhz)
        self.time_spinbox.valueChanged.connect(self.set_laser_frequency)
        
        self.show()

    def closeEvent(self, event):
        np.savez_compressed('spectroscopy', self.x_data, self.y_data)
        np.savetxt(self.output_filename_1, np.column_stack((self.x_data, self.y_data)), delimiter=',')
        self.api.stop_acquisition()
        event.accept()

    def set_acquisition_time(self, value):
        self.acquisition_time_in_seconds = value    
    
    def set_laser_frequency(self, value):
        self.laser_mhz = value  
        self.x_data = linspace(0, 1000 / self.laser_mhz, 256)
        self.setWindowTitle('Spectroscopy ' + str(self.laser_mhz) + ' MHz')
    
    def start_acquisition(self):
        self.start_button.setEnabled(False)
        #self.api.set_firmware("firmwares\\spectroscopy_simulator_" + str(self.laser_mhz) + "MHz.flim")
        self.api.set_firmware("firmwares\\spectroscopy_" + str(self.laser_mhz) + "MHz.flim")
        self.api.acquire_spectroscopy(
            laser_frequency_mhz=self.laser_mhz,
            acquisition_time_seconds=self.acquisition_time_in_seconds
        )
        self.stop_button.setEnabled(True)
        
    def stop_acquisition(self):
        self.stop_button.setEnabled(False)
        self.api.stop_acquisition()
        self.y_data = np.zeros(256)
        self.points_received = 0
        self.start_button.setEnabled(True)
        #self.stop_button.setEnabled(True)#provalo con il setup collegato
        
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


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    exit(app.exec())
