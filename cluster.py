import threading 
from threading import Thread
import socket
import time
import sys


class MyQueue:
    def __init__(self): # initialize a "queue" using a list
        self.queue = []
    def add(self, x): # add an element to the queue
        self.queue.append(x)
    def popleft(self): # remove the leftmost element from the queue to simulate a FIFO data structure
        return self.queue.pop(0)
    def sort(self): # sort the queue
        self.queue.sort()
    def print_queue(self):
        print(f"Sorted queue: {self.queue}")
    

class Producer(Thread):
    def __init__(self, client, queue, lock, full, empty):
        Thread.__init__(self) # constructor of the thread class
        self.client = client # client connection
        self.process_queue = queue # shared queue
        self.lock = lock # global lock
        self.full = full # semaphore
        self.empty = empty # semaphore
        

    def run(self):
        while True:
            mensaje = self.client.recv(1024).decode() # receive the message from the edevice
            if mensaje == "END": # terminating message, meaning there are no more processes
                 
                # critical region
                self.lock.acquire() # locking critical region, cannot be pulled out by the scheduler
                self.process_queue.add(None) # Add two None values(one for each consumer), to let them know
                self.process_queue.add(None) # there are no other process
                self.lock.release() 
                self.full.release() # release full two times because we are filling two slots in the queue
                self.full.release() # in this case, signals that there are two less open spaces
                break # break out of the while when there are no more processes
                # end of critical region

            print(f"Mensaje recibido: {mensaje}") # debbuging print to ensure all messages are received correctly
            # signal the edevice back so it sends another message
            _, cpu_time = mensaje.split(":") # messages are in the format "ProcessName: CpuTime". extract the cpu time of each process
            item = int(cpu_time) # conver the cpu time, from string to int

            # critical region
            self.empty.acquire() # one less empty space, since we are adding to the queue
            self.lock.acquire() # locking critical region, cannot be pulled out by the scheduler
            # print(f"Producer is Adding to queue: {item}") # making sure the items are added correctly
            self.process_queue.add(item) # add the cpu time of the process to the queue
            self.process_queue.sort() # sort the queue to simulate a SJF scheduler
            self.lock.release() 
            self.full.release()

class Consumer(Thread):
    def __init__(self, name, queue, lock, full, empty):
        Thread.__init__(self)
        self.name = name # Consumer's name
        self.process_queue = queue # shared queue
        self.lock = lock # global lock
        self.full = full # semaphore
        self.empty = empty # semaphore
        
    def run(self):
        consumed_time = 0
        while True:
            # critical region
            
            self.full.acquire() # one less occupied slot in the queue
            self.lock.acquire() # ensure only one thread at a time can modify the queue 

            item = self.process_queue.popleft() # pop the leftmost element from the queue
            # print(f"{self.name} esta Popping del queue: {item}") # debugging message

            if item == None: # conditional to jump out of critical region if what was popped is None, indicates no more processes
                # print(f"No more processes in the queue, {self.name} ending") # debbuging message
                self.lock.release() 
                self.empty.release() # signals the Producer thread that there is an empty space where a new item can be added
                break

            print(f"{self.name}: esta ejecutando proceso de tiempo: {item}") # debugging message
            self.lock.release()
            self.empty.release() # signals the Producer thread that there is an empty space where a new item can be added
            time.sleep(item) # simulates executing the process
            consumed_time += item
        print(f"{self.name} consumió {consumed_time} del CPU")
        # print(f"{self.name} sali") # indicator that the thread finished

def main():
    N = 10
    port = int(sys.argv[1])
    process_queue = MyQueue()  # Queue to hold the processes
    lock = threading.Lock() # lock 
    full = threading.Semaphore(0)  # No slots occupied
    empty = threading.Semaphore(N)  # N empty slots

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))  # Only accepts connections from the local machine
    server.listen(1)

    print(f"Servidor está escuchando en el puerto {port}")

    client, address = server.accept()
    print(f"Conexión establecida con {address}")

    # initialize Producer and Consumer Threads
    producer = Producer(client, process_queue, lock, full, empty)
    consumer1 = Consumer("Consumer 1", process_queue, lock, full, empty)
    consumer2 = Consumer("Consumer 2", process_queue, lock, full, empty)
        

    # Start producer and consumer threads
    producer.start()
    consumer1.start()
    consumer2.start()

    # Wait for all threads to finish
    producer.join()
    consumer1.join()
    consumer2.join()

    client.close() # close connection

if __name__ == "__main__":
    main()
