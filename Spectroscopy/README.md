# Spectroscopy

Here you can find the commented code used in [Spectroscopy](/Spectroscopy/spectroscopy.py) example

##### Needed libraries
  
```

  import matplotlib
  from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
  from matplotlib.figure import Figure
  from numpy import linspace

  matplotlib.use('Qt5Agg')

  import numpy as np
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

This class defines the main GUI window by setting its size, position and title, together with the x and y axes of the 2D plot where the fluorescence lifetime decay curve is shown.

On the x axis the laser period (in nanoseconds) is decomposed in 256 bins. On the y axis we have the counts of the photons falling in each bin, so what is displayed is the number of photons having a certain delay from the laser's pulse with 50-100 picoseconds resolution, depending on the pulsed laser's repetition rate. 

Also the laser frequency and the acquisition time of the experiment are set. The GUI window is completed with a start and stop button used to control the start and stop of the acquisition, a label to show the current number of photons received and a timer to refresh the plot every 100 ms.

```

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
        
        self.show()        
		
```
  
##### Methods
  
In the same class the method *closeEvent* is defined to save as npz file the data acquired after we stop the acquisition:
  
```

def closeEvent(self, event):
        np.savez_compressed('spectroscopy', self.x_data, self.y_data)
        self.api.stop_acquisition()
        event.accept()
		
```

Methods *set_acquisition_time* and *set_laser_frequency* are used to set the value of the acquisition time of the experiment and the laser frequency from the GUI:

```

def set_acquisition_time(self, value):
        self.acquisition_time_in_seconds = value    
    
def set_laser_frequency(self, value):
        self.laser_mhz = value
		
```
  
The *start_acquisition* method starts when pressing the start button and it is flashed the firmware for spectroscopy acquisition mode on the FPGA.
  
The *stop_acquisition* method starts when pressing the stop button to stop the acquisition of data from the FPGA. After the stop button is pressed the data in the histogram are reset, and also the number of received point is reset to zero, so that you can restart the acquisition by pressing again the start button. 
  
  
```

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
		self.points_received = 0
        self.start_button.setEnabled(True)
             
```
  
The *receive_point* method takes in input the following parameters:
  
* <b>channel</b>: channel from which the data are acquired 
* <b>time_bin</b>: digital bin within the laser period. As the laser period was decomposed in 256 bins, time_bin can be any integer value from 0 to 255 
* <b>micro_time</b>: variable representing the time bin in nanoseconds
* <b>monotonic_counter</b>: digital value accounting for the time passed from the beginning of the acquisition 
* <b>macro_time</b>: variable expressed in nanoseconds representing the time passed from the beginning of the acquisition
  
![input parameters](/images/mic-mac.jpg "parameters")
  
 
The *y_data* array is updated at the *time_bin* index by incrementing its value by 1. Also the number of points received is incremented by 1 for each photon received.
 
```

def receive_point(self, channel, time_bin, micro_time, monotonic_counter, macro_time):    
        self.mutex.lock()
        self.y_data[time_bin] += 1
        self.points_received += 1
        self.mutex.unlock()
            
```
 
A plot is made with the data stored in the *x_data* and *y_data* arrays and is updated with new data every 100 milliseconds by connecting the timeout signal of the timer to the *refresh_histogram* method:
 
```

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
		
```


In the file [Spectroscopy_post_processing.ipynb](/Spectroscopy/Spectroscopy_post_processing.ipynb) contained in this folder you can find some examples of how to process spectroscopy data saved from the experiment to extract additional informations and parameters.
 