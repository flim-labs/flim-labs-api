# flim_labs_api

## What is it? 

[flim_labs_api](/Flim_labs_api/flim_labs_api.py) is a Python API developed for controlling, acquiring and displaying <b>time tagged fluorescence photons' data</b> streamed from a data acquisition card based on FPGA technology in order to perform real time <b>Fluorescence Lifetime Imaging (FLIM) and Spectroscopy applications</b>.
Overall, this API sets up a communication system between Python and a FLIM data acquisition system based on FPGA that can receive data in various modes and store it for processing.

The complete FLIM kit developed by FLIM LABS for performing Fluorescence Lifetime Spectroscopy and Imaging looks like this:

![FLIM kit](/images/kit_1.jpg "Kit")

1. Fiber-coupled picosecond pulsed laser module

2. FLIM data acquisition card

3. Single-photon SPAD detector

4. FLIM studio software


For more informations on the single products you can check [FLIM LABS](https://www.flimlabs.com/) website.

## How to get it 

You can install flim_labs_api and the requested dependencies with the following *pip* command:

```
pip install flim_labs_api

```

## How to install drivers 

The drivers allowing the communication with the FPGA are pre-installed in your computer when running the *pip command* above.

If you want to manually install them you can find them inside the [drivers](/drivers) folder of this repo. The drivers' installers are put in two sub-folders containing the installers for x86 and x64 architectures respectively.


## Main features 

In the API five different acquisition modes are specified:

| Acquisition mode | Description |
|----------|----------|
| <b>Unset</b> | This is the default value of acquisition mode |
| <b>Photons_tracing</b> | Acquires the number of fluorescence photons in 100 microseconds time bins |
| <b>Spectroscopy</b> | Acquires the number of fluorescence photons in 50-100 picoseconds time bins (depending on the pulsed laser's frequency) and reconstruct the fluorescence lifetime decay curve |
| <b>Measure_frequency</b> | Acquires the frequency of the laser's pulses with a precision of tens/hundreds of Hz for repetition rates of tens of MHz|
| <b>Raw_data</b> | Acquires and saves the data coming from the FPGA as binary files without processing |


## Firmwares 

In order to perform the different acquisition modes it is necessary to flash the appropriate firmware on the FPGA.

You can find a list of available firmwares in the folder [firmwares](/firmwares) of this repo. 


## How to use it

It is possible to find some [examples](/examples) here showing how to use flim_labs_api in all the acquisition modes.

In the API the class <b>FlimLabsApi</b> is defined to provide an interface to control and communicate with a FPGA device. The class has several methods, including:

* <b>receiver_task</b> is a method that runs in the receiver_thread and receives messages from a ZeroMQ socket connection. The received messages are then parsed based on the acquisition mode and added to a queue for processing. This method has no input parameters.

* <b>consumer_task</b> is a method that runs in the consumer_thread. It listens to the queue, retrieves messages from it, and then calls the consumer_handler method if it exists. If acquisition_mode is Photons_tracing, Measure_frequency, or Spectroscopy, the data is decoded and passed to the consumer_handler method.This method also checks if the acquisition time has been reached, and if so, it stops acquisition by calling the stop_acquisition method.                                                         

* <b>stop_acquisition</b> is a method that stops the acquisition process by killing the processes. This method has no input parameters

* <b>set_firmware</b> is a method that sets the firmware of the FPGA. This method has in input the parameter *firmware* representing the firmware to be flashed on the FPGA to perform the desired acquisition mode 

* <b>_acquire_from_reader</b> this private method starts the threads receiver_thread and consumer_thread by starting the receiver_task and consumer_task methods. Then, it starts the flim-processor and sends a command to the flim-processor to receive the acquisition mode. It sends the command arguments to the flim-processor, which includes firmware, output file, chunk size, chunks, and additional arguments


## Examples 

1. <b>Spectroscopy</b></li> 
  
[spectroscopy.py](/examples/spectroscopy.py) is an implementation of *flim_labs_api* for spectroscopy acquisition mode. You can use *spectroscopy.py* connecting with a SMA connector the single photon detector to channel 1 of the data acquisition card.

With *spectroscopy.py* the laser period is divided in 256 time bins, and the single fluorescence photon events falling in each bin, recorded by a detector and time-tagged with tens/hundreds of picoseconds precision by the data acquisition card, are counted and passed to a 2D histogram to reconstruct the profile of the fluorescence lifetime decay curve.

For instance, if the pulsed laser is set with a repetition frequency of 80 MHz, that corresponds to a laser period of 12.5 nanoseconds, then time bins of 0.048 nanoseconds (48 picoseconds) are created and the number of photons falling in each 48 picoseconds time bin will be passed to the histogram.
  
For immediate reference, the code for *spectroscopy* use of the API  is reported and commented in the folder [Spectroscopy](/Spectroscopy).
  
This is an example of what is obtained using *spectroscopy.py* to reconstruct the fluorescence lifetime decay curve of a coumarin sample (1,5 micrograms/ml):
 
![Fluorescence lifetime decay curve of a coumarin sample](/images/spectroscopy_1.png "Spectroscopy on a coumarin sample")
 
The data are also saved as binary files for further visualization and processing.
 
  
2. <b>Measure-frequency</b>

[measure-frequency](/examples/measure-frequency.py) is an implementation of flim_labs_api for the measure_frequency acquisition mode. It measures the frequency of the laser pulses from the channel *sync in* of the FPGA.

Using *measure-frequency.py* code it is possible to achieve a precision of tens/hundreds of Hz for laser's frequencies of tens of MHz. 
 
The code for the *measure-frequency* use of the API, for immediate reference, is reported and commented in the folder [Measure frequency](/Measure_frequency).
 
This is an example of what is obtained to measure a pulsed laser's frequency of 80 MHz:

![80 MHz laser's frequency measurement](/images/frequency-meter_1.png "Frequency meter")
  

3. <b>Photons_tracing</b>

[photons_tracing](/examples/photons_tracing.py) is an example of using flim_labs_api for acquiring and displaying photons tracing data. You can acquire the data from all the 12 channels of the FPGA in this example.
 
The channels' map of the data acquisition card for the *photons_tracing* acquisition mode is the following: 

![Map of channels](/images/image_1.png "Channels map")

The code for the *photons_tracing* use of the API is reported and commented in the folder [Photons_tracing](/Photons_tracing) for immediate reference.

This is an example of what is obtained using *photons_tracing.py* to check the intensity of fluorescence photons in 100 microseconds time bins for a coumarin sample (1,5 micrograms/ml):
 
![Fluorescence photons' intensity for 100 microseconds bins](/images/photons_tracing_1.png "Photons tracing")
 
The data are also saved as binary files for further visualization and processing.


4. <b>Raw_data</b> 

[acquire_raw_data](/examples/acquire_raw_data.py)is an example of using flim_labs_api to acquire the data coming from the FPGA without processing and save them as .bin file.
You just have to flash the firmware for the acquisition mode you're interested in and specify the size in MB of the data you want to acquire.

The code for the *acquire_raw_data* use of the API is reported and commented in the folder [Acquire_raw_data](/Acquire_raw_data) for immediate reference.




















