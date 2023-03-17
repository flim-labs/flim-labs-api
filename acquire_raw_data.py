from flim_labs_api import FlimLabsApi

api = FlimLabsApi()
api.acquire_raw_data('firmwares\\photons_tracing_simulator.flim', 'file-test.bin', 32)
