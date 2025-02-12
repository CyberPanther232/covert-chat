from cryptography.fernet import Fernet

file_info = "files/test.txt:1200"
filepath = file_info.split(":")[0]
filesize = int(file_info.split(":")[1])
filename = filepath.split("/")[::-1][0]

print(filepath)
print(filesize)
print(filename)
