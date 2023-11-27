import socket, threading, time, pickle, random

class LamportLamportProcess(threading.Thread):
    def __init__(self, process_id: int, num_processes: int) -> object:
        self._process_id = process_id
        self._num_processes = num_processes
        super().__init__()