import socket
import threading
import time
import pickle
import random, sys

def send_message(destination, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(destination)
        s.sendall(pickle.dumps(message))

def receive_message(socket_conn):
    data = socket_conn.recv(1024)
    return pickle.loads(data)

class LamportAlgorithm(threading.Thread):
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.num_processes = num_processes
        self.logical_clock = [0] * num_processes
        self.in_critical_section = False
        self.request_queue = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 8000 + process_id))
        self.server_socket.listen(5)
        super().__init__(daemon=True)

    def should_request(self):
        # Adjust this method based on the desired behavior
        # For example, you can use a probability factor
        return random.random() < 0.5  # Simulates a 50% chance of wanting to access the critical section

    def request_access(self):
        # If the random selection is True, then the process will request access to the critical section
        if self.should_request():
            self.in_critical_section = False
            self.logical_clock[self.process_id] += 1
            print(f'Process {self.process_id} requests access to the critical section.')

            # Send the request to any other process except this one (i.e., the process that is requesting access)
            for i in range(self.num_processes):
                if i != self.process_id:
                    message = {'type': 'request', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                    send_message(('localhost', 8000 + i), message)

            # Add this process to the request queue. Responses from other messages will arrive later
            self.request_queue.append(self.process_id)

            # Wait untill all the other processes have responded
            while len(self.request_queue) < self.num_processes - (1 if self.num_processes > 1 else 0):
                time.sleep(1)

            self.enter_critical_section()

    def enter_critical_section(self):
        print(f'Process {self.process_id} enters the critical section.')
        time.sleep(2)  # Simulate work in the critical section

        self.exit_critical_section()

    def exit_critical_section(self):
        print(f'Process {self.process_id} exits the critical section.')
        self.in_critical_section = False

        # To leave the critical section, send a release message to all other processes and remove them from the queue
        for p in self.request_queue:
            if p != self.process_id:
                message = {'type': 'release', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + p), message)
        
        self.request_queue = []

    def handle_message(self, message):
        if message['type'] == 'request':

            # Another process is requesting access to the critical section
            self.logical_clock = [max(local, remote) for local, remote in zip(self.logical_clock, message['clock'])]
            self.logical_clock[self.process_id] += 1

            # Send the response that allows the other process to enter the critical section
            if not self.in_critical_section or (self.in_critical_section and
                                                (message['clock'][self.process_id] < self.logical_clock[self.process_id]
                                                 or (message['clock'][self.process_id] == self.logical_clock[self.process_id]
                                                     and message['process_id'] < self.process_id))):
                response = {'type': 'response', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + message['process_id']), response)
            else:
                # This process cannot allow the other one to move on, just put the request on queue
                self.request_queue.append(message['process_id'])

        elif message['type'] == 'release':
            # Another process is releasing the critical section
            self.logical_clock = [max(local, remote) for local, remote in zip(self.logical_clock, message['clock'])]
            self.logical_clock[self.process_id] += 1

            # If there are other processes waiting, send a response to the first one in the queue
            if self.request_queue:
                next_in_queue = self.request_queue.pop(0)
                response = {'type': 'response', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + next_in_queue), response)
            else:
                self.in_critical_section = False
        
        elif message['type'] == 'response':
            # We have received a response from another process that help us to enter the critical section
            self.logical_clock = [max(local, remote) for local, remote in zip(self.logical_clock, message['clock'])]
            self.logical_clock[self.process_id] += 1

            # Add the process to the request queue
            self.request_queue.append(message['process_id'])

    def run(self):
        while True:
            client_socket, address = self.server_socket.accept()
            message = receive_message(client_socket)
            self.handle_message(message)

def main():
    num_processes = 3
    processes = []

    for i in range(num_processes):
        process = LamportAlgorithm(i, num_processes)
        processes.append(process)

    for t in processes:
        t.start()

    # Simulation: Processes decide whether to request access
    try:
        while True:
            time.sleep(1)
            for t in processes:
                t.request_access()
    except KeyboardInterrupt:
        print('Stopping simulation...')
        sys.exit(0)

if __name__ == "__main__":
    main()
