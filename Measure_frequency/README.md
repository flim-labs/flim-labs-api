# Measure frequency

Here you can find the commented code used in [measure-frequency](/Measure_frequency/measure-frequency.py) example

##### Needed libraries
 
```

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

from flim_labs_api import FlimLabsApi

```

##### Define the MainWindow class

The main GUI window is defined by setting its size, position and title. The interface is completed with a start button to start the acquisition and a label showing the measured frequency of the laser pulses.

```

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
		
```

##### Methods

The method *receive_measure* is called when a measurement is received from the frequency meter through the *FlimLabsApi* object. This method updates the *measure_label* with the measurement result and enables the *start_button*

```

def receive_measure(self, frequency):                 
        self.measure_label.setText('Measurement: ' + str(frequency) + ' MHz')
        self.measure_label.adjustSize()
        self.start_button.setEnabled(True)
        self.api.stop_acquisition()
        self.update()

```

The method *closeEvent* is called when the main window is closed. It stops the acquisition of data from the frequency meter.

```
	
def closeEvent(self, event):
			self.api.stop_acquisition()
			event.accept()
	
```

The method *start_meter* is called when the *start_button* is clicked. This method updates the *measure_label* with a message to indicate that the measurement is waiting, disables the *start_button*, sets the *firmware* for the frequency meter, and starts the acquisition of data.

```
	
def start_meter(self):                               
        self.measure_label.setText('Waiting for measure...')
        self.measure_label.adjustSize()
        self.start_button.setEnabled(False)
        self.api.set_firmware("firmwares\\frequency_meter.flim")
        self.api.acquire_measure_frequency()
        self.update()

```