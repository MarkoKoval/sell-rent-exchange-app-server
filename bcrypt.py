"""
import hashlib
p = open("test.png", "rb")
print(hashlib.sha3_256(p.encode()).hexdigest())
"""

from PIL import Image
import hashlib
import time

t = time.time()

"""
for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    print(md5hash.hexdigest())
"""
print(time.time()-t)
#b53ac8b4289f47ad093a8439bcd3b5c0e67181d87fa6996bdf4d64f9dabba1f9
for i in range(10000):
    m = "hasss"
    md = hashlib.sha3_256("hellefotggggggggggggggggggggggggg".encode())
    print(md.hexdigest())
#b87f88c72702fff1748e58b87e9141a42c0dbedc29a78cb0d4a5cd81
#8574df5fd952bb619da2e04265a727204540ca71fdebecf284c5690d


print(time.time()-t)