# Threads Assignment

David Méndez Rosa
801-21-5508

## Contents

This Assignment contains two executable files:

    1. edevice.py(Embedded Device)
        - Connects to the Cluster via TCP sockets.
        - Fetches process running on the local computer and sends them to the Cluster so it can execute them.
        - The edevice sends a process with the time it will take to execute(cpu time)
        - Between each message it sends, the edevice goes to sleep 1-3 seconds to ensure every message is received correctly by the Cluster
        - Once every message(Process_Name: Cpu_time) is sent, the edevice has finished its part and closes the connection from their part

    2. cluster.py
        - Main purpose is to compute process sent from the embedded device
        - Allows TCP connections only from the local machine and a given port, in this case Port = 60000
        - Only listens for 1 connection at a time
        - Contains 3 Classes:
            - MyQueue:
                - Initializes a list with some user-defined functions to mimic a queue. It has the following functions:
                    - add(x): adds an element x to the back of the "queue"
                    - popleft(): removes the leftmost element(first element)
                    - sort(): sorts the queue to mimic a SFJ scheduler
                    - print_queue(): displays the queue

            - Producer:
                - Creates a Producer thread with the client connection, shared queue, the lock and semaphores
                - Receives the messages sent from the edevice.
                - From the message, the cluster extracts the cpu time of the process and adds them to a queue so a consumer can consume the resource.
                - The producer, sorts the queue after every insertion to ensure that processes are executed in SJF.
                - After producing an item, the producer signals the consumer so they can begin to consume items as long as the queue is not empty

            - Consumer:
                - Creates a Consumer thread with the Consumer thread's name, shared queue, the lock, semaphores and hashmap that keeps track of the total time consumed by each Consumer
                - Once a product is available for consumption, it begins to execute a process given its CPU time
                - Once there are no more available products, the consumer waits for the producer to produce more items. Repeating this until the producer stops producing any items.
                - When the producer finishes completely, it adds None values to queue to let consumers know that there are no more process to be executed.
        - main():
            - Initializes global variables such as queue, lock, semaphores, and Consumer hashmap
            - Uses TCP sockets to create the connection between the edevice and cluster
            - Creates, starts and join the Producer and Consumer Threads
            - Display the total time consumed by every Consumer

    How to run the scripts:
    For both scripts you may use whichever port you want since it extracts the port from the command line. Since both files are on the same machine, the IP address is set to '127.0.0.1' by default.

    For the cluster.py:
        - python3 cluster.py 60000

    For the edevice.py:
        - python3 edevice.py 127.0.0.1 60000

    Example output:
        Todos los procesos se ejecutaron.
        Consumer 1 consumió 7 del tiempo del CPU
        Consumer 2 consumió 8 del tiempo del CPU

## Resources used
    -   StackOverflow
    -   Socket Programming in Python (https://realpython.com/python-sockets/)
    -   An Intro to Threading in Python (https://realpython.com/intro-to-python-threading/)
