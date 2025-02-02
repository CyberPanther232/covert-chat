import socket
import hashlib
import os
from cryptography.fernet import Fernet
from datetime import datetime
from _thread import *
import _ssl

IP = '127.0.0.1' # leave as blank string to listen on all addresses
PORT = 12346 # port number to bind socket
TIMER = 10 # Time in seconds
USER_DATABASE = 'users.csv' # user database
KEY = Fernet.generate_key()

class Secure_Channel:
    def __init__(self, user1, user2):
        self.user1, self.user2 = user1, user2

def encrypt_message(message, key):
    try:
        return Fernet(key).encrypt(message.encode())
    except Exception as e:
        print(f"Encryption Error: {e}")

def decrypt_message(message, key):
    try:
        return Fernet(key).decrypt(message.encode()).decode()
    except Exception as e:
        print(f"Decryption Error: {e}")

def log_message(message, user):
    with open(f"message_logs.txt", 'a') as log_file:
        log_file.write(f"<{user}>: {message} - {format_date(datetime.now())}\n")
    log_file.close()

def keygen():
    try:
        open('keyfile.key', 'wb').write(KEY)
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
    users.close()

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
                users.close()

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
                for user in online_users:
                    for k,v in user.items():
                        if uname == k:
                            print("Error... Login unsuccessful") # Covertly handles when users are already signed in
    
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

def client_thread(con, addr, uname, online_users):
    while True:
        try:
            message = decrypt_message(con.recv(2048).decode(), KEY)
            if message:
                print("<" + uname + ">: " + message)
                message_to_send = "<" + uname + ">: " + message
                
                if len(online_users) <= 1:
                    con.send(encrypt_message('<server>: No other users connected... Please try again later!',KEY))
                    
                elif message == "bye":
                    log_event(f"User {uname} disconnected!")
                    con.close()
                else:
                    log_message(message, uname)
                    broadcast(message_to_send, uname, online_users)

        except Exception as e:
            print(f"Exception: {e}")
            continue

def format_date(date):
    return datetime.strftime(date, '%m/%d/%y %H:%M:%S.%f')

def log_event(event):
    with open('log', 'a') as logfile:
        logfile.write(f'{event}' + ": " + f'{format_date(datetime.now())}\n')
    logfile.close()

def main():

    print("Starting up covert PypherText messaging...")
    print("Running user setup...")
    generate_user_database()
    print("Generating new keyfile...")
    keygen()

    try:

        try:
            open('log', 'x')
        except FileExistsError:
            pass

        with open('log', 'a') as logfile:
            logfile.write(f"Server started: {format_date(datetime.now())}")
        logfile.close()

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
                    uname = decrypt_message(con.recv(1024).decode(), KEY)
                    pswd = hashlib.sha512(decrypt_message(con.recv(1024).decode(), KEY).encode()).hexdigest()
                    
                    if validate_login(uname, pswd, online_users):

                        con.send(encrypt_message('Login Successful!', KEY))

                        log_event(f"Login Successful from {uname}")

                        online_users.append({uname : con})
                        
                        start_new_thread(client_thread, (con, addr, uname, online_users))


                    else:
                        con.send(encrypt_message('Login unsuccessful... Closing connection!', KEY))
                        log_event(f"Login attempt unsuccessful!")
                        con.shutdown(socket.SHUT_WR)
                        con.close()
                    

                except Exception as e:
                    print(e)
            except Exception as e:
                print(f"Socket Error: {e}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()