from ..models import Users
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import hashlib
from datetime import datetime
from django.utils import timezone
import time

# t = time.time()
"""
for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    """
# md5hash = hashlib.sha3_256("grgerger".encode())
# print(md5hash.hexdigest())
"""
from PIL import Image
import hashlib
import time

t = time.time()

for i in range(10):
    md5hash = hashlib.sha3_256(Image.open("7rK61.jpg").tobytes())
    print(md5hash.hexdigest())
"""

@csrf_exempt
def get_auth_token(id_):
    user = Users.objects.get(id=id_)
    return hashlib.sha3_256( (str(user.time_entered) + user.name + user.password_hash + user.email).encode()).hexdigest()

@csrf_exempt
def create_auth_token(user):
    user.time_entered = datetime.now(tz=timezone.utc)
    user.save()
    return hashlib.sha3_256( (str(user.time_entered) + user.name + user.password_hash + user.email).encode()).hexdigest()


@csrf_exempt
def login(request):

    print(5)
    print(1)

    v = hashlib.sha3_256(
        request.POST["password"].encode()).hexdigest()
    print(v)
    print(Users.objects.all().values_list('id', 'email',  'password_hash','location'))
    if request.method == "POST":
        try:
            print(request.POST)
            user = Users.objects.get(email=request.POST["email"])
        except Exception as e:
            print(e)
            return JsonResponse({"response": "Введіть коректні дані"}, content_type="application/json", status=400,safe=False)
        print(user.password_hash )
        print(v)
        print(user.password_hash == v)
        if user.password_hash == v:
            return JsonResponse({"id": user.id, "name": user.name, "token": create_auth_token(user)},
                            content_type="application/json",  safe=False, status =200)
        else:
            return JsonResponse(json.dumps({"response": "Введіть коректні дані"}), content_type="application/json",
                                status=400, safe=False)


@csrf_exempt
def register(request):

    if request.method == "POST":
        user, created = None,None
        try:
            user, created = Users.objects.get_or_create(email=request.POST["email"], name=request.POST["name"],
                                                        password_hash=hashlib.sha3_256(
                                                            request.POST["password"].encode()).hexdigest())
        except Exception as e:
            print(created)
            print(user)
            print(e)
            return JsonResponse(json.dumps({"response": e}), content_type="application/json", safe=400)
        status = 200 if created else 400
        response = {"id": user.id, "name": user.name, "token": create_auth_token(user)} if created else {
            "response": 'Вже є користувач з такими параметрами'}
        print(response)
        return JsonResponse(response, content_type="application/json", safe=False, status = status)
    return JsonResponse({})
# return JsonResponse(json.dumps({"response": "200"}), content_type="application/json", safe=False, status=200)
