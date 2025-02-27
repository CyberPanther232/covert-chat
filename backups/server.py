import socket
import hashlib
import os
from cryptography.fernet import Fernet # type: ignore
from datetime import datetime
from random import randint
from _thread import *
import _ssl

IP = '127.0.0.1' # leave as blank string to listen on all addresses
PORT = 12345 # port number to bind socket
TIMER = 10 # Time in seconds
USER_DATABASE = 'users.csv' # user database
KEY = Fernet.generate_key()
CHUNK_SIZE = 4096

class TransferTunnel:
    def __init__(self, user1, user2, command, ip, port=randint(60000,65535), file="none"):
        self.user1, self.user2, self.ip, self.port, self.command, self.file = user1, user2, ip, port, command, file

    def establish_connection(self):
        self.tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tsock.bind(self.ip, self.port)

        self.tsock.listen(10)
        conn, addr = self.tsock.accept()
        print("Connection established!")
        conn.send(encrypt_message("Connection established!"),KEY)

    def send_data(self):
        try:
            with open(self.file, 'rb') as readfile:
                while chunk := readfile.read(CHUNK_SIZE):
                    self.tsock.sendall(encrypt_data(chunk, KEY))
        except FileNotFoundError:
            print(f"Error: {self.file} not found!")
            socket.send(encrypt_message("Error: File not found", KEY))

def encrypt_message(message, key):
    try:
        return Fernet(key).encrypt(message.encode())
    except Exception as e:
        print(f"Encryption Error: {e}")

def encrypt_data(data, key):
    try:
        return Fernet(key).encrypt(data)
    except Exception as e:
        print(f"Encryption Error: {e}")

def decrypt_data(data, key):
    try:
        return Fernet(key).decrypt(data)
    except Exception as e:
        print(f"Data Decryption Error: {e}")
        return

def decrypt_message(message, key):
    try:
        return Fernet(key).decrypt(message).decode()
    except Exception as e:
        print(f"Decryption Error: {e}")
        return None  # Avoid exit, just return None

def send_file(socket, file, key):
    try:
        with open(file, 'rb') as readfile:
            while chunk := readfile.read(CHUNK_SIZE):
                socket.sendall(encrypt_data(chunk, key))
    except FileNotFoundError:
        print(f"Error: {file} not found!")
        socket.send(encrypt_message("Error: File not found", key))


def log_message(message, user):
    with open(f"message_logs.txt", 'a') as log_file:
        log_file.write(f"<{user}>: {message} - {format_date(datetime.now())}\n")

def keygen():
    try:
        open('./keyfile.key', 'wb').write(KEY)
    except Exception as e:
        print(f"Encryption key generation error: {e}")
        return None
    
def check_for_user(uname):

    user_exists = False

    with open(USER_DATABASE, 'r') as users:
        for line in users:
            stored_uname, pswd = line.split(',')
            if stored_uname == uname:
                print("User already exist!")
                user_exists = True
            else:
                pass

    return user_exists

def loggen():
    os.mkdir(f'server_logs')

def generate_user_database():
    try:
        open(USER_DATABASE, 'x')
    except FileExistsError:
        print("User database exists!")

    prompt = str(input("Would you like to add a new user: ")).lower()

    if prompt == 'y' or prompt == 'yes':
        while True:
            uname = str(input("Enter new username: "))
            pswd = str(input("Enter new password: "))

            if check_for_user(uname):
                print("Please enter a different username!")
            else:
                with open(USER_DATABASE, 'a') as users:
                    users.write(f"{uname},{hashlib.sha512(pswd.encode()).hexdigest()}\n")

                print("User created successfully!")
                prompt = str(input("Would you like to add another?")).lower()

                if prompt == 'y' or prompt == 'yes':
                    pass
                else:
                    break

def validate_login(uname, pswd, online_users):

    with open(USER_DATABASE, 'r') as users:
        for line in users:
            stored_uname, stored_hash = line.strip().split(',')
            if uname == stored_uname and pswd == stored_hash:
                online_users_dict = {user: con for d in online_users for user, con in d.items()}
                if uname in online_users_dict:
                    print("Error... Login unsuccessful")

                print(f"Login from user {uname} successful!")
                return True
            else:
                pass
    
        print(f"Failed login attempt! Closing connection...")
        return False
    users.close()

def broadcast(message, uname, online_users):
    for user in online_users:
        for k, v in user.items():
            if uname == k:
                pass
            else:
                v.send(encrypt_message(message, KEY))

def save_chat(chat_data, uname, message):
    pass

def client_thread(con, addr, uname, online_users):
    while True:
        try:
            enc_message = con.recv(CHUNK_SIZE)

            if not enc_message:
                print("Client response error...")
                online_users.remove({uname : con})
                con.close()
                return

            message = decrypt_message(enc_message, KEY)
            if message:

                print("<" + uname + ">: " + message)
                message_to_send = "<" + uname + ">: " + message
                
                if message.split(' ')[0].lower() == "pull":
                        try:
                            send_file(con, message.split(' ')[1], KEY)
                        except Exception as e:
                            print('Invalid pull command...')
                            pass
                
                # if len(online_users) <= 1:
                #     con.send(encrypt_message('<server>: No other users connected... Please try again later!',KEY))
                
                elif message.lower() == "bye":
                    log_event(f"User {uname} disconnected!")
                    print(f"{uname} has disconnected!")
                    con.close()
                    online_users.remove({uname : con})
                    break


                else:
                    log_message(message, uname)
                    # con.send(encrypt_message("Message received!", KEY))
                    broadcast(message_to_send, uname, online_users)

        except Exception as e:
            print(f"Exception: {e}")
            continue
    return 
def format_date(date):
    return datetime.strftime(date, '%m/%d/%y %H:%M:%S.%f')

def log_event(event):
    with open('log', 'a') as logfile:
        logfile.write(f'{event}' + ": " + f'{format_date(datetime.now())}\n')

def main():

    global chat_data
    chat_data = {}

    print("Starting up covert PypherText messaging...")
    print("Running user setup...")
    generate_user_database()
    print("Generating new keyfile...")
    keygen()
    print("Generated Key")

    try:

        try:
            open('log', 'x')
        except FileExistsError:
            pass

        with open('log', 'a') as logfile:
            logfile.write(f"Server started: {format_date(datetime.now())}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.bind((IP, PORT))
        print(f"Sock binded successfully to port {PORT}")

        try:
            sock.listen(TIMER)
            print(f"Listening for connection attempts on IP: {IP}...")
        except KeyboardInterrupt:
            exit()

        online_users = []

        while True:
            try:
                con, addr = sock.accept()
                print(f"Connection attempt from {addr}!")
                
                log_event('Connection attempt from a client!')

                con.send(encrypt_message('Please enter your login credentials', KEY))

                try:
                    uname = decrypt_message(con.recv(CHUNK_SIZE), KEY)
                    pswd = hashlib.sha512(decrypt_data(con.recv(CHUNK_SIZE), KEY)).hexdigest()
                    
                    if validate_login(uname, pswd, online_users):

                        con.send(encrypt_message('Login Successful!', KEY))

                        log_event(f"Login Successful from {uname}")

                        online_users.append({uname : con})
                        chat_data[uname] = []

                        try:
                            start_new_thread(client_thread, (con, addr, uname, online_users))
                        except Exception as e:
                            print(f"Error: {e}")
                            online_users.remove({uname : con})
                            con.close()

                    else:
                        con.send(encrypt_message('Login unsuccessful... Closing connection!', KEY))
                        log_event(f"Login attempt unsuccessful!")
                        con.shutdown(socket.SHUT_WR)
                        con.close()

                except Exception as e:
                    print(e)
                    con.close()
                    continue
            except Exception as e:
                print(f"Socket Error: {e}")
                continue

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()