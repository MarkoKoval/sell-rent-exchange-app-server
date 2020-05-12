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

"""
def register(request):
    if request.POST:
        Users.objects.create(user_name=request.POST["user_name"],
                             user_email = request.POST["user_email"],
                             user_password_hash= hashlib.sha3_256(request.POST["user_password"]))

    return JsonResponse({"registered": False})


def login(request):
    return render()
"""

#from .models import Document
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import base64

from django.core.files.base import ContentFile


def f():
    print("haha")


@csrf_exempt
def list1(request):
    if request.method == 'POST':
        """
        print(len(request.body))
        print(type(request.body))
        print(dir(request.body))
       # print(request.body.keys())
        print(request.body["get_d"])
       
        
        """
        print(request.POST["get_d"])
        i = json.loads( request.POST["get_d"])
        print(i)
        print(type(i))
        print(i["images"])
        print(type(i["images"]))
        """
        try:
            for j in i["images"]:
                format, imgstr = j["path"].split(';base64,')
                ext = format.split('/')[-1]

                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                newdoc = Document(docfile=data)
                newdoc.save()
        except Exception as E:
            print(E)

        """
        """
        try:
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
        except Exception as e:
            print(e)
        """
    print(1)
    #for i in Document.objects.all():
    #    print(i.docfile.path)
    return JsonResponse(json.dumps({"response": "200"}), content_type="application/json", safe=False)

    """
        if request.method == 'POST':
            print(len(request.POST))
            print(request.POST.keys())
            print(request.POST["dat"])
        """
    # print("Logging message", flush=True)
    # Handle file upload
    # print(131)
    # f()
    # print("haha")
    # print(request.method)
    """
    if request.method == 'POST':
            print(request.POST)
            print(request.FILES)
            print(len(request.FILES))
            print(request.FILES.keys())

            try:
                newdoc = Document(docfile = request.FILES['docfile'])
                newdoc.save()
            # Redirect to the document list after POST
            except Exception as e:
            """
    # return JsonResponse({"response": e})

    # Render list page with the documents and the form