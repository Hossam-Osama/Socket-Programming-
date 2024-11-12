import socket
import sys
import time

# Default HTTP port
DEFAULT_PORT = 8080

def client_connect(host, port=DEFAULT_PORT):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    print(f"Connected to server at {host}:{port}")
    return client

def client_get(client, file_path, host):
    start_time = time.time()  # Record the start time of the GET request
    request = f"GET /{file_path} HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n"
    client.sendall(request.encode('utf-8'))
    
    try:
        # Receive response
        response = b""
        while True:
            part = client.recv(4096)
            response += part
            if len(part) < 4096:
                break

        headers, _, body = response.partition(b"\r\n\r\n")
        print("Server headers:\n", headers.decode('utf-8'))

        with open(file_path, 'wb') as file:
            file.write(body)
        print(f"Saved GET response to {file_path}")
        
        end_time = time.time()  # Record the end time
        request_time = end_time - start_time  # Calculate the time taken for the request
        print(f"GET request time: {request_time:.4f} seconds")

    except socket.error as e:
        print(f"Socket error: {e}")

def client_post(client, file_path, host):
    try:
        # Read the file data to send
        with open(file_path, 'rb') as f:
            data = f.read()

        start_time = time.time()  # Record the start time of the POST request
        # Prepare the POST request
        request = (
            f"POST /{file_path} HTTP/1.1\r\n"
            f"Host: {host}\r\n"
            f"Content-Length: {len(data)}\r\n"
            "Connection: keep-alive\r\n\r\n"
        ).encode('utf-8') + data

        # Send the POST request to the server
        client.sendall(request)

        # Receive the server response
        response = client.recv(4096)
        print("Server response:\n", response.decode('utf-8', errors='ignore'))
        
        end_time = time.time()  # Record the end time
        request_time = end_time - start_time  # Calculate the time taken for the request
        print(f"POST request time: {request_time:.4f} seconds")

    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except socket.error as e:
        print(f"Socket error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <host> [port]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT

    client = client_connect(host, port)

    try:
        while True:
            command = input("Enter command (get <file_path> | post <file_path> | exit): ").strip().lower()
            if command == "exit":
                print("Closing connection.")
                break

            if command.startswith("get "):
                file_path = command.split(" ", 1)[1]
                client_get(client, file_path, host)
            elif command.startswith("post "):
                file_path = command.split(" ", 1)[1]
                client_post(client, file_path, host)
            else:
                print("Invalid command. Use 'get <file_path>', 'post <file_path>', or 'exit'.")
    except socket.timeout:
        print("Connection timed out.")
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        client.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()
