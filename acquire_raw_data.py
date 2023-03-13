from flim_labs_api import FlimLabsApi

api = FlimLabsApi()
api.set_firmware('firmwares\\naio.flim')
api.acquire_raw_data(32, 100)
