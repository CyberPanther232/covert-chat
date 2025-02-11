import socket
from cryptography.fernet import Fernet
import _ssl
import os
import time

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
    
def pull_file(socket, key):

    file_info = decrypt_data(socket.recv(1024), key)

    filepath = file_info.split(":")[0]
    filesize = file_info.split(":")[1]
    filename = filepath.split("/")[:-1]

    try:
        try:
            open(filename, 'x')
        except:
            pass
        with open(filename, 'wb') as newfile:
            bytes_received = 0
            while bytes_received < filesize:
                chunk = decrypt_data(socket.recv(1024),key)
                if not chunk:
                    break
                newfile.write(chunk)
                bytes_received += len(chunk)
            print(f"{filename} pulled succesfully!")
            return
    except Exception as e:
        print(e)
        return

def getkey(ip):
    try:
        os.system(f"curl -s -O http://{ip}:8000/keyfile.key")
        return open('keyfile.key', 'rb').read()
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
                print(decrypt_message(sock.recv(1024).decode(), key))
                uname = str(input("Enter username: "))
                sock.send(encrypt_message(uname, key))
                pswd = str(input("Enter password: "))
                sock.send(encrypt_message(pswd, key))
                login_reply = decrypt_message(sock.recv(1024).decode(), key)
                
                print(login_reply)
                
                if login_reply != "Login unsuccessful... Closing connection!":
                    while True:
                        msg = str(input("\nEnter Message: "))
                        sock.send(encrypt_message(msg, key))
                        print(msg[0:4])
                        if msg[0:4].lower() == "pull":
                            pull_file(sock, key)
                        else:
                            reply = decrypt_message(sock.recv(2048).decode(), key)
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