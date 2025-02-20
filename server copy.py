import socket
import threading
from cryptography.fernet import Fernet
import hashlib
import select
import time
import os

# Dictionary to store online users
online_users = {}
lock = threading.Lock()
server_running = True  # Global server running flag
KEY = ""
START_TIME = time.time()

try:
    open('test_users.csv', 'x')
except FileExistsError:
    pass

def broadcast_message(message, sender_username):
    """Send a message to all connected clients except the sender."""
    formatted_message = f"<{sender_username}>: {message}"

    with lock:
        for username, conn in online_users.items():
            if username != sender_username:
                try:
                    conn.send(formatted_message.encode())
                except:
                    del online_users[username]  # Remove disconnected clients

def calc_runtime(start, end):
    runtime = end - start
    if runtime < 60:
        return f"{runtime:.2f} seconds"
    elif runtime < 3600:
        minutes = runtime / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = runtime / 3600
        return f"{hours:.2f} hours"

def send_direct_message(message, sender_username, recipient_username):
    """Send a direct message to a specific user."""
    formatted_message = f"DM from <{sender_username}>: {message}"

    with lock:
        recipient_conn = online_users.get(recipient_username)
        if recipient_conn:
            recipient_conn.send(formatted_message.encode())
            sender_conn = online_users[sender_username]
            sender_conn.send(f"DM to <{recipient_username}>: {message}".encode())
        else:
            sender_conn = online_users[sender_username]
            sender_conn.send(f"Error: User <{recipient_username}> is not online.".encode())

def manage_online_users():
    """Thread function to monitor and display online users."""
    while server_running:
        with lock:
            disconnected = [user for user, conn in online_users.items() if conn.fileno() == -1]
            for user in disconnected:
                del online_users[user]
        time.sleep(5)

def handle_client(client_socket, username):
    """Handles individual client communication."""
    with lock:
        online_users[username] = client_socket

    try:
        while server_running:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            # Check if it's a direct message
            if message.startswith('@'):
                recipient_username, msg = message[1:].split(' ', 1)
                send_direct_message(msg, username, recipient_username)
            else:
                print(f"[{username}] {message}")
                broadcast_message(message, username)

    except:
        pass
    finally:
        with lock:
            del online_users[username]
        client_socket.close()
        print(f"{username} disconnected.")

def server_management():
    """Function to handle server commands like echo, users, and shutdown."""
    global server_running
    while True:
        command = input("\nServer>> ")
        
        if command[0:4] == "echo":
            print(command[5:])

        elif command == "users":
            print("Currently online users:", online_users)
        
        elif command == "clear":
            os.system("clear")
            
        elif command == "logs":
            os.system("less log")
            
        elif command == "help":
            print("Commands:\necho: Repeats any text/characters after the echo command")
            print("users: Displays the current online users")
            print("clear: Clears the window of text")
            print("logs: Displays the logfile")
            print("useradd: Adds a user to the accepted users file")
            print("userdel: Deletes a user from the accepted user file list")
            print("runtime: Displays the active server runtime")
            print("genkey: Generates a new encryption key")
            print("shutdown: Shuts the server down")
            
        elif command == "useradd":
            username = str(input("Enter username: "))
            password = str(input("Enter password: "))
            print(f"Creating new user '{username}'!")
            with open('test_users.csv', 'r') as userfile:
                users = userfile.readlines()
            
            exists = True if any(user == username for user in users) else False
            
            if not exists:
                with open('test_users.csv', 'a') as userfile:
                    userfile.write(f"{username},{hashlib.sha512(password.encode()).hexdigest()}\n")
                print("New user created successfully!")
            else:
                print(f"User with username '{username}' already exists!")
            
        elif command == "userdel":
            username = str(input("Enter username: "))
            with open('test_users.csv', 'r') as userfile:
                users = userfile.readlines()
            
            updated_users = [user for user in users if user.split(',')[0] != username]
            
            if len(updated_users) == len(users):
                print(f"No user with username '{username}' found...")
                pass
            else:
                with open('test_users.csv', 'w') as userfile:
                    userfile.writelines(updated_users)
                print(f"User '{username}' deleted successfully!")
        
        elif command == "runtime":
            end_time = time.time()
            print(f"The server has been running for {calc_runtime(START_TIME, end_time)}")
                
        elif command == "genkey":
            print("Generating new encryption key!")
            global KEY
            KEY = Fernet.generate_key()
            
            with open('keyfile.key', 'wb') as keyfile:
                keyfile.write(KEY)
            
            print("Key generated and loaded successfully! Make sure to send encryption key to users!")
            
        elif command == "shutdown":
            print("Shutting server down!")
            server_running = False
            # Close all client connections
            with lock:
                for client_socket in online_users.values():
                    client_socket.close()
            break  # Exit server management loop
    
        else:
            print("Invalid command...")

def accept_connections(server_socket):
    """Accept new client connections."""
    while server_running:
        read_sockets, _, _ = select.select([server_socket], [], [], 0.5)
        if read_sockets:
            client_socket, client_address = server_socket.accept()
            print(f"New connection from {client_address}")

            # Send a prompt for the username
            client_socket.send("Enter your username: ".encode())
            username = client_socket.recv(1024).decode()
            client_socket.send("Enter your password: ".encode())
            password = client_socket.recv(1024).decode()
            print(username)
            print(client)
            online_users[username] = client_socket

            # Start a new thread for the client
            client_thread = threading.Thread(target=handle_client, args=(client_socket, username))
            client_thread.daemon = True
            client_thread.start()

def start_server():
    """Main function to start the chat server."""
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5555))
    server.listen(5)

    # Start the online users manager thread
    threading.Thread(target=manage_online_users, daemon=True).start()

    # Start the server management thread for commands like shutdown
    threading.Thread(target=server_management, daemon=True).start()

    print("Server started. Waiting for connections...")

    # Accept new client connections in the main thread
    accept_connections(server)

    server.close()
    print("Server shut down.")

if __name__ == "__main__":
    start_server()
