import socket
import time
import sys
import matplotlib.pyplot as plt
from threading import Thread

# Default server host and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8080


def client_get_requests(num_requests):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_HOST, SERVER_PORT))
    
    # Send 'GET' request 'num_requests' times
    for _ in range(num_requests):
        request = "GET /testfile.txt HTTP/1.1\r\nHost: {}\r\nConnection: keep-alive\r\n\r\n".format(SERVER_HOST)
        client.sendall(request.encode('utf-8'))
        client.recv(4096)  
    
    client.close()


def performance_test(client_count):
    threads = []
    start_time = time.time()


    for _ in range(client_count):
        thread = Thread(target=client_get_requests, args=(1,))
        threads.append(thread)
        thread.start()

    
    for thread in threads:
        thread.join()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Test completed for {client_count} clients. Total time: {total_time:.4f} seconds.")
    return total_time

# Run the performance test for different client counts and record results
def run_performance_tests():
    client_counts = [10, 100, 1000, 10000]
    times = []

    for client_count in client_counts:
        print(f"Starting performance test with {client_count} clients...")
        total_time = performance_test(client_count)
        times.append(total_time)

    # Plot the results
    plt.figure(figsize=(10, 6))
    plt.plot(client_counts, times, marker='o', linestyle='-', color='b')
    plt.xlabel('Number of Clients')
    plt.ylabel('Time Delay (seconds)')
    plt.title('Performance Test: Time Delay vs Number of Clients')
    plt.grid(True)
    plt.xscale('log')  
    plt.yscale('log')  
    plt.show()

if __name__ == "__main__":
    run_performance_tests()
