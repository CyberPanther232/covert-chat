import socket
from cryptography.fernet import Fernet
import _ssl

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

def getkey():
    try:
        return open('keyfile.key', 'rb').read()
    except Exception as e:
        print(f"Key file error: {e}")
        return None

def main():

    ip = ""
    port = 0

    while True:
        try:
            print(f"IP: {ip} | PORT: {port}")

            new_ip = str(input("Enter IP: "))
            new_port = int(input("Enter Port: "))
            
            if new_ip != "":
                ip = new_ip
            
            if new_port != "":
                port = new_port

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            key = getkey()

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
                return None

        except Exception as e:
            print(f"Error: {e}")
            next

        

if __name__ == "__main__":
    main()