from django.shortcuts import render
from .models import *
# Create your views here.
import hashlib
from django.http import JsonResponse
"""
from PIL import Image
import hashlib
import time

t = time.time()

for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    print(md5hash.hexdigest())

print(time.time()-t)
"""


def register(request):
    if request.POST:
        Users.objects.create(user_name=request.POST["user_name"],
                             user_email = request.POST["user_email"],
                             user_password_hash= hashlib.sha3_256(request.POST["user_password"]))

    return JsonResponse({"registered": False})


def login(request):
    return render()
