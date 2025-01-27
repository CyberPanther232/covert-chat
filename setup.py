from __future__ import absolute_import, unicode_literals
import os
import time
import base64
from LSBSteg import LSBSteg
import cv2

STEGFILE = 'sneaky_snake.jpg'
CLIENT = 'client.py'
OUTFILE = 'python.png'


print("Running steganography setup script!")

print("Extracting client contents and encoding to base64!")
client_contents = base64.b64encode(open(CLIENT).read().encode(encoding='ascii'))

print(f"Uploading client contents to image {STEG}!")
steg = LSBSteg(cv2.imread(STEGFILE))
img_enc = steg.encode_binary(client_contents)
cv2.imwrite(OUTFILE,img_enc)

print("Completed!")