import socket
import threading
import hashlib
import os

def receive_messages(client_socket):
    """Handles receiving messages from the server."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"{message}")
        except:
            print("Disconnected from server.")
            break

def send_messages(client_socket):
    """Handles sending messages to the server."""
    while True:
        message = input()
        if message.lower() == "exit":
            client_socket.send("EXIT".encode())
            break
        client_socket.send(message.encode())

def start_client():
    server_ip = "127.0.0.1"  # Change this to the server's IP
    server_port = 5555

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Receive server's username request
    print(client_socket.recv(1024).decode(), end="")
    username = input()
    password = input()
    client_socket.send(username.encode())
    client_socket.send(hashlib.sha512(password.encode()).hexdigest())
    os.system("Clear")
    print("Connection successful!")
    print("Start by typing a message printing enter!")

    # Start threads for sending and receiving
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    send_messages(client_socket)

    client_socket.close()

if __name__ == "__main__":
    start_client()
