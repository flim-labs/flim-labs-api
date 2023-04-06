Here you can find the commented code used in [acquire_raw_data](/Acquire_raw_data/acquire_raw_data.py) example:

Import the *FlimLabsApi* class and the *generate_unique_filename* method from *flim_labs_api*. 

``` 

from flim_labs_api import FlimLabsApi, generate_unique_filename

api = FlimLabsApi()

``` 

Select the name of the .bin file in which you save the data, the size in MegaBytes of the file and flash the firmware on the FPGA for the desired acquisition mode.

Finally call the method *acquire_raw_data* from *flim_labs_api* to acquire the data and save them with the specified options. 

``` 

output_filename = 'acquisition_raw.bin'
firmware = 'firmwares\\photons_tracing_simulator.flim'
acquisition_size_in_MB = 25

api.acquire_raw_data(firmware, generate_unique_filename(output_filename, "datetime"),
                     acquisition_size_in_MB)

```
