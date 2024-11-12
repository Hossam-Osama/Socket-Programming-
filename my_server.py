import socket
import threading
import os
import time

# Server configuration
HOST = '127.0.0.1'
PORT = 8080
BASE_DIR = './'  # Directory to serve files from
# Timeout configuration
IDLE_TIMEOUT_BASE = 30  # Base timeout in seconds
IDLE_TIMEOUT_ACTIVE_LOAD = 10  # Timeout during high load
HIGH_LOAD_THRESHOLD = 5  # Number of clients considered "high load"
active_connections = []

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        active_connections.append(conn)
        while True:
            start_time = time.time()  # Record the start time of the request

            # Adjust timeout based on current load before each recv
            active_count = len(active_connections)
            if active_count > HIGH_LOAD_THRESHOLD:
                print(f"IDLE_TIMEOUT_ACTIVE_LOAD - {active_count} active clients")
                conn.settimeout(IDLE_TIMEOUT_ACTIVE_LOAD)
            else:
                conn.settimeout(IDLE_TIMEOUT_BASE)

            try:
                request = conn.recv(4096)
                if not request:
                    break  # Client closed connection

                request_str = request.decode('utf-8', errors='ignore')  # Ignore non-UTF-8 characters
                lines = request_str.splitlines()
                request_line = lines[0].split()

                if len(request_line) < 2:
                    break  # Invalid request format

                method = request_line[0]
                path = request_line[1].lstrip('/')

                # Handle GET request
                if method == 'GET':
                    file_path = os.path.join(BASE_DIR, path)
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as file:
                            content = file.read()
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Length: {}\r\n"
                            "Connection: keep-alive\r\n\r\n"
                        ).format(len(content)).encode('utf-8') + content
                    else:
                        response = (
                            "HTTP/1.1 404 Not Found\r\n"
                            "Content-Length: 0\r\n"
                            "Connection: keep-alive\r\n\r\n"
                        ).encode('utf-8')

                # Handle POST request
                elif method == 'POST':
                    headers_end = request_str.find('\r\n\r\n')
                    if headers_end == -1:
                        print("Invalid POST request, missing headers")
                        break
                    headers = request_str[:headers_end]
                    
                    # Retrieve Content-Length
                    content_length = 0
                    for line in headers.splitlines():
                        if line.lower().startswith("content-length"):
                            content_length = int(line.split(":")[1].strip())

                    # Receive the body based on Content-Length
                    body = request[headers_end+4:]
                    while len(body) < content_length:
                        body += conn.recv(content_length - len(body))

                    if len(body) != content_length:
                        print(f"Error: Expected {content_length} bytes, but got {len(body)}")
                        break

                    # Save the received body (e.g., file upload)
                    file_path = os.path.join(BASE_DIR, path)
                    with open(file_path, 'wb') as file:
                        file.write(body)  # Write binary data to a file

                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Length: {}\r\n"
                        "Connection: keep-alive\r\n\r\n"
                    ).format(len(body)).encode('utf-8')

                # Send response
                conn.sendall(response)

                end_time = time.time()  # Record the end time
                response_time = end_time - start_time  # Calculate response time
                # print(f"Response time for {addr}: {response_time:.4f} seconds")

            except socket.timeout:
                print(f"Connection with {addr} timed out.\n")
                break

    except Exception as e:
        print(f"Error with client {addr}: {e}")
    finally:
        print(f"Connection with {addr} closed.")
        conn.close()
        active_connections.remove(conn)

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server running on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            # Start a new thread for each client
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

if __name__ == "__main__":
    start_server()
