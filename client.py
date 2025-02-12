import socket
from cryptography.fernet import Fernet
import _ssl
import os
import time
import requests

CHUNK_SIZE = 4096

def encrypt_message(message, key):
    try:
        return Fernet(key).encrypt(message.encode())
    except Exception as e:
        print(f"Encryption Error: {e}")

def decrypt_message(message, key):
    try:
        return Fernet(key).decrypt(message.encode()).decode()
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
    file_info = decrypt_data(s.recv(CHUNK_SIZE), key).decode()
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
        
def getkey(ip):
    try:
        response = requests.get(f"http://{ip}:8000/keyfile.key", timeout=5)
        response.raise_for_status()
        with open("keyfile.key", "wb") as f:
            f.write(response.content)
        return response.content
    except Exception as e:
        print(f"Key file error: {e}")
        time.sleep(5)
        return None


def main():

    ip = ""
    port = 0

    while True:
        try:
            print(f"IP: {ip} | PORT: {port}")

            new_ip = str(input("Enter IP: "))
            new_port = input("Enter Port: ")
            
            if new_ip != "":
                ip = new_ip
            
            if new_port != "":
                port = int(new_port)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            key = getkey(ip)

            if key == None:
                print("No key found... Please try again.")
                exit(0)
            else:
                print("Key retrieved successfully!")

            try:
                sock.connect((ip, port))
                print(decrypt_message(sock.recv(CHUNK_SIZE).decode(), key))
                uname = str(input("Enter username: "))
                sock.send(encrypt_message(uname, key))
                pswd = str(input("Enter password: "))
                sock.send(encrypt_message(pswd, key))
                login_reply = decrypt_message(sock.recv(CHUNK_SIZE).decode(), key)
                
                print(login_reply)
                
                if login_reply != "Login unsuccessful... Closing connection!":
                    while True:
                        msg = str(input("\nEnter Message: "))
                        sock.send(encrypt_message(msg, key))
                        if msg[0:4].lower() == "pull":
                            pull_file(sock, key)
                        else:
                            sock.send(encrypt_message(msg, key))
                            reply = decrypt_message(sock.recv(CHUNK_SIZE).decode(), key)
                            if reply:
                                print(reply)
                                
                            elif reply == "Secure Channel Setup":
                                pass
                            else:
                                pass
                else:
                    sock.close()
                    
            except Exception as e:
                print(f"Connection Error: {e}")
                pass
                # return None

        except Exception as e:
            print(f"Error: {e}")
            next

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system('rm keyfile.key')
        exit()