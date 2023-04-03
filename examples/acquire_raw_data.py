from flim_labs_api import FlimLabsApi

api = FlimLabsApi()
api.set_firmware('firmwares\\test.bit')
api.acquire_raw_data(32, 100)
