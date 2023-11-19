import socket
import threading
import time
import pickle

import socket
import threading
import time
import pickle

# Function for sending messages
def send_message(destination, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(destination)
        s.sendall(pickle.dumps(message))

# Function for receiving messages
def receive_message(socket_conn):
    data = socket_conn.recv(1024)
    return pickle.loads(data)

# Implementation of Lamport's Mutual Exclusion Algorithm
class LamportAlgorithm:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.num_processes = num_processes
        self.logical_clock = [0] * num_processes
        self.in_critical_section = False
        self.request_queue = []

    def request_access(self):
        self.in_critical_section = False
        self.logical_clock[self.process_id] += 1

        for i in range(self.num_processes):
            if i != self.process_id:
                message = {'type': 'request', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + i), message)

        while len(self.request_queue) < self.num_processes - 1:
            time.sleep(1)

        self.enter_critical_section()

    def enter_critical_section(self):
        print(f'Process {self.process_id} enters the critical section.')
        time.sleep(2)  # Simulate work in the critical section

        self.exit_critical_section()

    def exit_critical_section(self):
        print(f'Process {self.process_id} exits the critical section.')
        self.in_critical_section = False

        for i in range(self.num_processes):
            if i != self.process_id:
                message = {'type': 'release', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + i), message)

    def handle_message(self, message):
        if message['type'] == 'request':
            self.logical_clock = [max(local, remote) for local, remote in zip(self.logical_clock, message['clock'])]
            self.logical_clock[self.process_id] += 1

            if not self.in_critical_section or (self.in_critical_section and
                                                (message['clock'][self.process_id] < self.logical_clock[self.process_id]
                                                 or (message['clock'][self.process_id] == self.logical_clock[self.process_id]
                                                     and message['process_id'] < self.process_id))):
                response = {'type': 'response', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + message['process_id']), response)
            else:
                self.request_queue.append(message['process_id'])

        elif message['type'] == 'release':
            self.logical_clock = [max(local, remote) for local, remote in zip(self.logical_clock, message['clock'])]
            self.logical_clock[self.process_id] += 1

            if self.request_queue:
                next_in_queue = self.request_queue.pop(0)
                response = {'type': 'response', 'clock': self.logical_clock.copy(), 'process_id': self.process_id}
                send_message(('localhost', 8000 + next_in_queue), response)
            else:
                self.in_critical_section = False


# Function to manage a process's connection
def handle_connection(client_socket, lamport):
    while True:
        message = receive_message(client_socket)
        lamport.handle_message(message)


# Main function
def main():
    num_processes = 10  # Set the number of processes
    processes = []

    for i in range(num_processes):
        lamport_algorithm = LamportAlgorithm(i, num_processes)
        t = threading.Thread(target=handle_connection, args=((('', 8000 + i)), lamport_algorithm))
        t.start()
        processes.append(t)

    # Simulation: The first two processes request access to the critical section
    time.sleep(2)
    processes[0].request_access()
    time.sleep(1)
    processes[1].request_access()

    for t in processes:
        t.join()


if __name__ == "__main__":
    main()
