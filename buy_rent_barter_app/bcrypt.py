from PIL import Image
import hashlib
import time
from django.utils import timezone
import pytz
from django.utils import timezone
from django.utils import timezone






"""
for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    """
md5hash = hashlib.sha3_256("grgerger".encode())
print(md5hash.hexdigest())

t = time.time()
"""
for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    """
md5hash = hashlib.sha3_256("grgerger".encode())
print(md5hash.hexdigest())
"""
from PIL import Image
import hashlib
import time

t = time.time()

for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    print(md5hash.hexdigest())
"""