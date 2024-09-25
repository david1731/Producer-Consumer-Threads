import socket
import random
import time
import sys
import subprocess

min_cpu_time = 3
max_cpu_time = 8

def get_processes(limit):
    process_names = []
    try:
        # Execute the ps commands with its arguments and stores the results(process names)
        # ps = lists current running process
        # -e = shows the information of every process
        # '-o comm' = only displays the command name
        result = subprocess.run(['ps', '-eo', 'comm='], stdout=subprocess.PIPE, text=True)
        process_output = result.stdout.strip().split('\n')

        # Remove duplicates and store unique process names
        process_names = list(set(process_output))[:limit]
    except Exception as e:
        print(f"Error occurred while getting process names: {e}")

    return process_names

def create_and_send_jobs(address, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # creating socket type IPV4 anda TCP
    try:
        client.connect((address,port)) # connecting to the cluster's ip and port
        # print(f"Conexion exitosa con servidor:{address} y port:{port}")
    except Exception as e: # error handling
        print(f"No se pudo hacer una conexion con el servidor: {e}")


    processes = get_processes(3) # will only get 10 process running on computer, adjust the paramaters for desired number of processes
    
    for process in processes:
        cpu_time = random.randint(min_cpu_time,max_cpu_time) # generate a random cpu_time for each process
        msg = f"{process}:{cpu_time}" # preparing the message to send to the cluster

        try:
            client.sendall(msg.encode()) # send the message to the cluster
        except:
            print(f"No se pudo enviar el mensaje")
        time.sleep(random.randint(1,3)) # 1 second delay between each message
    exitString = "END" # termination message
    client.sendall(exitString.encode()) # send termination messages
    client.close() # close connection
    # print("Conexion cerrada")

if __name__ == "__main__":
    address = sys.argv[1]
    port = int(sys.argv[2])
    create_and_send_jobs(address,port)

