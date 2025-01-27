from cryptography.fernet import Fernet

key = Fernet.generate_key()

print(key)

open('keyfile.key', 'wb').write(key)

message = 'Hello World!'

print(Fernet(key).encrypt(message.encode('utf-8')))
