from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

from flim_labs_api import FlimLabsApi


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(512, 512, 1024, 1024)
        self.setWindowTitle('Frequency meter')

        self.api = FlimLabsApi()
        self.api.set_consumer_handler(self.receive_measure)

        self.start_button = QPushButton('Start', self)
        self.start_button.move(5, 5)
        self.start_button.clicked.connect(self.start_meter)

        self.measure_label = QLabel(self)
        self.measure_label.move(5, 40)
        self.measure_label.setText('Press start to measure')
        self.measure_label.adjustSize()

        self.show()

    def receive_measure(self, frequency):
        self.measure_label.setText('Measurement: ' + str(frequency) + ' MHz')
        self.measure_label.adjustSize()
        self.start_button.setEnabled(True)
        self.api.stop_acquisition()
        self.update()

    def closeEvent(self, event):
        self.api.stop_acquisition()
        event.accept()

    def start_meter(self):
        self.measure_label.setText('Waiting for measure...')
        self.measure_label.adjustSize()
        self.start_button.setEnabled(False)
        self.api.set_firmware("firmwares\\frequency_meter.flim")
        self.api.acquire_measure_frequency()
        self.update()


if __name__ == '__main__':
    print("Starting application")
    app = QApplication([])
    window = MainWindow()
    exit(app.exec())
