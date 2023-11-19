# Lamport Mutual Exclusion
Python's implementation of Lamport Mutual Exclusion Algorithm.

## Introduction
The Lamport's Mutual Exclusion Algorithm is designed to allow multiple concurrent processes to access a shared resource safely and orderly, ensuring that only one process at a time can execute the critical section of the code. The critical section is the part of a program where the process manipulates shared resources, and it is crucial to ensure mutual exclusion to avoid race conditions and unpredictable outcomes.

## Lamport's Logical Clocks
1. Initialization: Each process has a vector of logical clocks initialized to zero. For example, if there are N processes, each vector will have N components.
2. Event Generation: Whenever a process performs an operation, its logical clock is incremented in the corresponding position.

## Requesting Access to the Critical Section
1. Request: When a process wants to access the critical section, it sends a message containing its request and its logical clock to all other processes.
2. Receiving the Request: When a process receives a request, it updates its own logical clock by taking the maximum value of each component of its vector and the corresponding values received in the request.
3. Response: The process responds to the request only if it is safe to do so. Safety is determined by comparing the request timestamps with the local timestamps. If the remote process has higher priority or if the timestamps are the same but the ID of the remote process is lower, the local process waits. Otherwise, it sends a response message to the requesting process.

## Releasing the Critical Section
1. Release: When a process has finished executing the critical section, it sends a message to all other processes indicating that it has completed access to the resource.
2. Updating the Clock: Upon receiving the release message, each process updates its own logical clock by taking the maximum of each component of its vector and the corresponding value in the release message.
