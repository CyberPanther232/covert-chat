import socket
from cryptography.fernet import Fernet # type: ignore
import _ssl
import os
import time
from random import randint
# import requests

CHUNK_SIZE = 4096

def encrypt_message(message, key):
    try:
        return Fernet(key).encrypt(message.encode())
    except Exception as e:
        print(f"Encryption Error: {e}")

def decrypt_message(message, key):
    try:
        return Fernet(key).decrypt(message).decode()
    except Exception as e:
        print(f"Message Decryption Error: {e}")
        return
    
def decrypt_data(data, key):
    try:
        return Fernet(key).decrypt(data)
    except Exception as e:
        print(f"Data Decryption Error: {e}")
        return
    
def pull_file(s, key):
    file_info = decrypt_data(s.recv(CHUNK_SIZE), key)
    try:
        filepath, filesize = file_info.split(":")
        filename = os.path.basename(filepath)
        filesize = int(filesize)
    except ValueError:
        print("Invalid file info format!")
        return

    try:
        with open(filename, 'wb') as newfile:
            bytes_received = 0
            while bytes_received < filesize:
                chunk = decrypt_data(s.recv(CHUNK_SIZE), key)
                if not chunk:
                    break
                newfile.write(chunk)
                bytes_received += len(chunk)
        print(f"{filename} pulled successfully!")
    except Exception as e:
        print(f"File Transfer Error: {e}")

def encrypt_data():
    pass
        
def getkey(ip):
    try:
        # response = requests.get(f"http://{ip}:8000/keyfile.key", timeout=5)
        # response.raise_for_status()
        with open("keyfile.key", "rb") as f:
            return f.read()
        #     f.write(response.content)
        # return response.content
    except Exception as e:
        print(f"Key file error: {e}")
        time.sleep(5)
        return None

class TransferTunnel:
    def __init__(self, user1, user2, key, command, ip, port=randint(60000,65535), file="none"):
        self.user1, self.user2, self.key, self.ip, self.port, self.command, self.file = user1, user2, key, ip, port, command, file

    def establish_connection(self):
        self.tsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tsock.bind(self.ip, self.port)

        self.tsock.listen(10)
        conn, addr = self.tsock.accept()
        print("Connection established!")
        conn.send(encrypt_message("Connection established!"),self.key)

    def send_data(self):
        try:
            with open(self.file, 'rb') as readfile:
                while chunk := readfile.read(CHUNK_SIZE):
                    self.tsock.sendall(encrypt_data(chunk, self.key))
        except FileNotFoundError:
            print(f"Error: {self.file} not found!")
            socket.send(encrypt_message("Error: File not found", self.key))

def main():

    ip = ""
    port = 0

    while True:
        try:
            print(f"IP: {ip} | PORT: {port}")

            new_ip = str(input("Enter IP: "))
            new_port = input("Enter Port: ")
            
            if new_ip != "":
                octets = new_ip.split('.')
                if len(octets) < 4 or len(octets) >= 5:
                    ip = ""
                    print("Invalid IP...")
                    continue
                else:
                    count = 0
                    valid_ip = False
                    for octet in octets:
                        count += 1
                        if count == 4 and int(octet) < 254 and int(octet) >= 1 and len(octet) > 0 and len(octet) <= 3:
                            valid_ip = True
                        else:
                            valid_ip = False

                        if int(octet) < 255 and int(octet) >= 1 and len(octet) > 0 and len(octet) <= 3:
                            valid_ip = True
                        else:
                            valid_ip = False
    
                    if valid_ip:
                        ip = new_ip
                    else:
                        print("Invalid IP")
                        ip = ""
                        continue

            try:
                if new_port != "":
                    if int(new_port) > 65535 or int(new_port) <= 10000:
                        print("Invalid port number! Please enter a port between 9999 and 65535 and try again!")
                        port = ""
                        continue
                    else:    
                        port = int(new_port)
                else:
                    print("Invalid port number! Please enter a port between 9999 and 65535 and try again!")
                    port = ""
                    continue

            except ValueError:
                print("Invalid port value! Please enter and try again!")
                port = ""
                continue

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            key = getkey(ip)

            if key == None:
                print("No key found... Please try again.")
                exit(0)
            else:
                print("Key retrieved successfully!")

            if port != "":

                try:
                    sock.connect((ip, port))
                    print(decrypt_message(sock.recv(CHUNK_SIZE), key))
                    uname = str(input("Enter username: "))
                    sock.send(encrypt_message(uname, key))
                    pswd = str(input("Enter password: "))
                    sock.send(encrypt_message(pswd, key))
                    login_reply = decrypt_message(sock.recv(CHUNK_SIZE), key)
                    
                    print(login_reply)
                    
                    if login_reply != "Login unsuccessful... Closing connection!":
                        os.system("clear")
                        while True:
                            msg = str(input("\nEnter Message: "))
                            if msg != "":
                                sock.send(encrypt_message(msg, key))
                                if msg[0:4].lower() == "pull":
                                    pull_file(sock, key)

                                elif msg.lower() == "bye":
                                    print("Logging out of server!")
                                    sock.close()
                                    break
                                else:
                                    reply = decrypt_message(sock.recv(CHUNK_SIZE), key)
                                    if reply:
                                        print(reply)
                                        
                                    elif reply == "Secure Channel Setup":
                                        pass
                                    else:
                                        pass
                            else:
                                print("No message sent...")
                    else:
                        sock.close()
                    
                except Exception as e:
                    print(f"Connection Error: {e}")
                    pass
                    # return None
            else:
                print("Invalid connection values... Please try again!")
                continue

        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # os.system('rm keyfile.key')
        exit()