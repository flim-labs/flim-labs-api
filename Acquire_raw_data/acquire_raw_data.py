from flim_labs_api import FlimLabsApi, generate_unique_filename

api = FlimLabsApi()

output_filename = 'acquisition_raw.bin'
firmware = 'firmwares\\photons_tracing_simulator.flim'
acquisition_size_in_MB = 25

api.acquire_raw_data(firmware, generate_unique_filename(output_filename, "datetime"),
                     acquisition_size_in_MB)
