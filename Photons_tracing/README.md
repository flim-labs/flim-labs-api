# Photons tracing

Here you can find the commented code used in [Photons_tracing](/Photons_tracing/photons_tracing.py) GUI

##### Needed libraries

```

import matplotlib
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from numpy import linspace

matplotlib.use('Qt5Agg')

from PyQt5.QtCore import QTimer, QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel

from flim_labs_api import FlimLabsApi

```

##### Define the MplCanvas class

This class creates the object *Figure* with the specified width, height, and dpi values that will be used for plotting the data.

```

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)
		
```

##### Define the MainWindow class

The MainWindow class initializes the GUI window, sets up the acquisition time and the acquisition channels and creates a chart for displaying the photon tracing data. It also sets up a timer for refreshing the chart, a button for starting the data acquisition, and a label for displaying the current phase of the acquisition:
The start button triggers an acquisition of photon tracing data by calling the method *acquire_photons_tracing* from the *flim_labs_api* library

```

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setGeometry(512, 512, 1024, 1024)
        self.setWindowTitle('Photons tracing')

        self.api = FlimLabsApi()
        self.api.set_consumer_handler(self.receive_data)

        self.chart = MplCanvas(self, width=12, height=5, dpi=100)
        self.setCentralWidget(self.chart)

        self.slice = 1 * SLICE_SECONDS        #?
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

        

        self.show()
		
```

##### Methods

The *closeEvent* method is called when the user closes the application. It stops the acquisition of data, saves the data to a file, and closes the application.

```

    def closeEvent(self, event):
        self.api.stop_acquisition()
        np.savez_compressed('photons_tracing', data=self.data)
        event.accept()
		
```

The *receive_data* method takes in input the parameter *row_data* , which is a list containing the photon counts for each channel in a particular time bin, and then appends the corresponding photon count to the channel's data.
The variable *self.rows_received* is then incremented to keep track of the number of rows of data received.

```

def receive_data(self, row_data):
        self.mutex.lock()
        for i, channel in enumerate(self.channels):
            
            self.data[i].append(row_data[i])
        self.rows_received += 1
        self.mutex.unlock()
		
```

The *refresh_histogram* method is called every 1 millisecond by a QTimer instance to update the histogram with new data.

```
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

```