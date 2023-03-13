import subprocess
import threading
import time
import traceback
from queue import Queue, Empty

import psutil
import zmq

MB = 262144


class AcquisitionMode:
    UNSET = 'unset'
    PHOTONS_TRACING = 'photons-tracing'
    SPECTROSCOPY = 'spectroscopy'
    MEASURE_FREQUENCY = 'measure-frequency'
    RAW_DATA = 'raw-data'


class FlimLabsApi:
    def __init__(self):
        self._kill_process_if_exists("flim-processor.exe")
        self._kill_process_if_exists("flim-reader.exe")

        self.acquisition_time_seconds = None
        self.acquisition_mode = AcquisitionMode.UNSET
        self.queue = Queue()

        self.z_sub = zmq.Context().socket(zmq.SUB)
        self.z_sub.RCVTIMEO = 1000
        self.z_sub.connect("tcp://localhost:5556")
        self.z_sub.setsockopt(zmq.SUBSCRIBE, b"")

        self.z_commands = zmq.Context().socket(zmq.REQ)
        self.z_commands.connect("tcp://localhost:5550")

        self.receiver_thread = None
        self.consumer_thread = None
        self.consumer_handler = None
        self.firmware = None
        self.enable_consumer = False
        self.enable_consumer_lock = threading.Lock()
        self.enable_receiver = False
        self.enable_receiver_lock = threading.Lock()

        self.photons_tracing_bin_count = 0

    def receiver_task(self):
        while True:
            self.enable_receiver_lock.acquire()
            if not self.enable_receiver:
                self.enable_receiver_lock.release()
                break
            self.enable_receiver_lock.release()
            try:
                message = self.z_sub.recv()
                message = message.decode('utf-8')

                if message == 'exp':
                    continue

                message = message[1:-1].split(',')

                match self.acquisition_mode:
                    case AcquisitionMode.PHOTONS_TRACING:
                        message = list(map(int, message))
                    case AcquisitionMode.MEASURE_FREQUENCY:
                        message = list(map(float, message))[0]
                    case AcquisitionMode.SPECTROSCOPY:
                        message = (
                            int(message[0]),
                            int(message[1]),
                            float(message[2]),
                            int(message[3]),
                            float(message[4])
                        )
                    case _:
                        raise Exception("[PY-API] receiver_task: Invalid acquisition mode=" + self.acquisition_mode)

                self.queue.put(message)

            except zmq.error.Again:
                pass
            except Exception as e:
                print(e)
        print("[PY-API] Receiver thread stopped.")

    def consumer_task(self):
        while True:
            self.enable_consumer_lock.acquire()
            if not self.enable_consumer:
                self.enable_consumer_lock.release()
                break
            self.enable_consumer_lock.release()
            try:
                message = self.queue.get(timeout=0.1)

                if self.consumer_handler:
                    match self.acquisition_mode:
                        case AcquisitionMode.PHOTONS_TRACING:
                            self.photons_tracing_bin_count += 1
                            # every time_bin is 100 microseconds seconds
                            if self.photons_tracing_bin_count > self.acquisition_time_seconds * 10_000:
                                print("[PY-API] Acquisition time reached. Stopping acquisition.")
                                print("[PY-API] Acquisition time: " + str(
                                    self.acquisition_time_seconds) + " s, bin_count: " + str(
                                    self.photons_tracing_bin_count))
                                self.stop_acquisition()
                                break
                            self.consumer_handler(message)
                        case AcquisitionMode.MEASURE_FREQUENCY:
                            self.consumer_handler(message)
                        case AcquisitionMode.SPECTROSCOPY:
                            channel, time_bin, micro_time, monotonic_counter, macro_time = message
                            if macro_time > self.acquisition_time_seconds * 1_000_000_000:
                                print("[PY-API] Acquisition time reached. Stopping acquisition.")
                                print("[PY-API] Acquisition time: " + str(
                                    self.acquisition_time_seconds) + " s, macro_time: " + str(macro_time) + " ns")
                                self.stop_acquisition()
                                break
                            self.consumer_handler(channel, time_bin, micro_time, monotonic_counter, macro_time)
                        case AcquisitionMode.RAW_DATA:
                            pass
                        case _:
                            raise Exception("[PY-API] consumer_task: Invalid acquisition mode=" + self.acquisition_mode)
            except Empty:
                pass
            except Exception as e:
                print("[PY-API] Consumer error: " + str(e))
                traceback.print_exc()
        print("[PY-API] Consumer thread stopped.")

    @staticmethod
    def _kill_process_if_exists(process_name):
        if process_name is None:
            return
        processes = list(p.name() for p in psutil.process_iter())
        if process_name in processes:
            try:
                subprocess.Popen(["taskkill", "/F", "/T", "/IM", process_name])
            except:
                pass

    def stop_acquisition(self):
        print("[PY-API] Stopping acquisition")
        self._kill_process_if_exists("flim-processor.exe")
        self._kill_process_if_exists("flim-reader.exe")
        self.enable_receiver_lock.acquire()
        print("[PY-API] Disabling receiver thread")
        self.enable_receiver = False
        self.enable_receiver_lock.release()
        self.enable_consumer_lock.acquire()
        print("[PY-API] Disabling consumer thread")
        self.enable_consumer = False
        self.enable_consumer_lock.release()
        print("[PY-API] Acquisition stopped.")

    def set_firmware(self, firmware):
        print("[PY-API] Setting firmware to " + firmware)
        self.firmware = firmware

    def set_consumer_handler(self, handler):
        self.consumer_handler = handler

    def acquire_raw_data(self, chunk_size: int, chunks: int):
        self.acquisition_mode = AcquisitionMode.RAW_DATA
        self._acquire_from_reader(chunk_size, chunks)

    def acquire_measure_frequency(self):
        self.acquisition_mode = AcquisitionMode.MEASURE_FREQUENCY

        self._acquire_from_reader(32, 1)

    def acquire_photons_tracing(self, channels: list[int], acquisition_time_seconds: int = 300):
        if channels is None:
            raise Exception("Channel list is None")
        if len(channels) > 12:
            raise Exception("Maximum number of channels is 12")
        for channel in channels:
            if channel < 1 or channel > 12:
                raise Exception("Channel number must be between 1 and 12")
        if len(channels) == 0:
            raise Exception("Channel list is empty")
        if len(channels) != len(set(channels)):
            raise Exception("Channel list contains duplicated")

        self.acquisition_mode = AcquisitionMode.PHOTONS_TRACING
        self.photons_tracing_bin_count = 0
        self.acquisition_time_seconds = acquisition_time_seconds

        channels_str = ""
        for channel in channels:
            channels_str += str(channel) + ","
        channels_str = channels_str[:-1]

        self._acquire_from_reader(1024, 1024 * 800, channels_str)

    # def acquire_raw_data(self, firmware: str, output_file: str, chunk_size: int, chunks: int):
    #     self.acquisition_mode = AcquisitionMode.RAW_DATA
    #     print("[PY-API] Executing flim-reader.exe " + firmware + " " + output_file)
    #     subprocess.run(["flim-reader.exe", firmware, output_file, str(chunk_size), str(chunks), "big", "disable-streaming"], shell=True)

    def acquire_spectroscopy(self, laser_frequency_mhz: int, acquisition_time_seconds: int):
        self.acquisition_mode = AcquisitionMode.SPECTROSCOPY

        if laser_frequency_mhz != 40 and laser_frequency_mhz != 80:
            raise Exception("Laser frequency must be 40 or 80 MHz")

        if acquisition_time_seconds <= 0:
            raise Exception("Acquisition time must be greater than 0 seconds")

        self.acquisition_time_seconds = acquisition_time_seconds

        self._acquire_from_reader(1024, 1024 * 800, str(laser_frequency_mhz))

    def _acquire_from_reader(self, chunk_size: int, chunks: int, additional_args: str = None):
        try:
            output_file = "output_" + time.strftime("%Y%m%d-%H%M%S") + ".bin"
            self.enable_receiver_lock.acquire()
            print("[PY-API] Enabling receiver thread")
            self.enable_receiver = True
            self.enable_receiver_lock.release()
            self.enable_consumer_lock.acquire()
            print("[PY-API] Enabling consumer thread")
            self.enable_consumer = True
            self.enable_consumer_lock.release()
            self.receiver_thread = threading.Thread(target=self.receiver_task)
            self.consumer_thread = threading.Thread(target=self.consumer_task)
            self.receiver_thread.start()
            self.consumer_thread.start()
            self.queue = Queue()
            print("[PY-API] Starting flim-processor")
            subprocess.Popen(["flim-processor.exe"])
            print("[PY-API] Sending command to flim-processor")
            self.z_commands.send_string(self.acquisition_mode)
            args_response = self.z_commands.recv_string()
            if args_response != "args":
                raise Exception("Unexpected response from flim-processor")
            print("[PY-API] Sending command args to flim-processor")
            commands = self.firmware + ";" + output_file + ";" + str(chunk_size) + ";" + str(chunks)
            if additional_args is not None:
                commands += ";" + additional_args
            self.z_commands.send_string(commands)
            print("[PY-API] Command args sent, commands=" + commands)
            ok = self.z_commands.recv_string()
            print("[PY-API] Response from flim-processor: " + ok)
        except Exception as e:
            print("[PY-API] Error: " + str(e))
            # print stacktrace
            traceback.print_exc()
