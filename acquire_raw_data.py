import os.path

from flim_labs_api import FlimLabsApi

api = FlimLabsApi()

filename = 'acquisition.bin'
firmware = 'firmwares\\photons_tracing_simulator.flim'
acquisition_size_in_MB = 25

index = 1
while os.path.exists(filename):
    extension = os.path.splitext(filename)[1]
    basename = os.path.splitext(filename)[0]
    filename = f'{basename}-{index}' + (f'{extension}' if extension != '' else '')
    index += 1
    break

api.acquire_raw_data(firmware, filename, acquisition_size_in_MB)
