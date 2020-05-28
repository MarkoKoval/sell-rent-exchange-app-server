from ..models import Users
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import hashlib
from datetime import datetime
from django.utils import timezone
from django.db import transaction

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
@transaction.atomic
def get_auth_token(id_):
    user = Users.objects.get(id=id_)
    data = (str(user.time_entered) + user.name + user.password_hash + user.email)
    print("get:")
    print(data)
    return hashlib.sha3_256( data.encode()).hexdigest()

@csrf_exempt
@transaction.atomic
def create_auth_token(user):
    user.time_entered = datetime.now(tz=timezone.utc)
    user.save()
    var =  (str(user.time_entered) + user.name + user.password_hash + user.email).encode()
    print("create:")
    print(var)
    return hashlib.sha3_256( var).hexdigest()


@csrf_exempt
@transaction.atomic
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
          #  user.role = "Адміністратор"
          #  user.save()
            return JsonResponse({ "role": user.role,"id": user.id, "name": user.name, "token": create_auth_token(user)},
                            content_type="application/json",  safe=False, status =200)
        else:
            return JsonResponse(json.dumps({"response": "Введіть коректні дані"}), content_type="application/json",
                                status=400, safe=False)


@csrf_exempt
@transaction.atomic
def register(request):

    if request.method == "POST":
        user, created = None,None
        try:
            user, created = Users.objects.get_or_create(role="",email=request.POST["email"], name=request.POST["name"],
                                                        password_hash=hashlib.sha3_256(
                                                            request.POST["password"].encode()).hexdigest())
        except Exception as e:
            print(created)
            print(user)
            print(e)
            return JsonResponse(json.dumps({"response": e}), content_type="application/json", safe=400)
        status = 200 if created else 400
        response = {"id": user.id, "name": user.name, "role": user.role, "token": create_auth_token(user)} if created else {
            "response": 'Вже є користувач з такими параметрами'}
        print(response)
        return JsonResponse(response, content_type="application/json", safe=False, status = status)
    return JsonResponse({})
# return JsonResponse(json.dumps({"response": "200"}), content_type="application/json", safe=False, status=200)

import threading
from ..notify_email import email_notify
@csrf_exempt
@transaction.atomic
def change_role(r,id):
    print(3333)
    try:
       auth = json.loads(r.POST["auth"])
       print(auth)
       print(get_auth_token(auth["id"]))
       if auth["token"] != get_auth_token(auth["id"]):
           print("change_role")
           return  JsonResponse({"answer": "Немає прав"},status=400)
       #print(r.POST)
       user =  Users.objects.get(id=id)
       if user.role == "Звичайний":
           user.role = "Віп"
       elif user.role == "Віп":
           user.role = "Звичайний"
       user.save()
    except Exception as e:
        print(e)
        return JsonResponse({},status=400)
    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Зміна ролі кориcтувача на " + user.role, user.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({},status=200)

@csrf_exempt
@transaction.atomic
def get_rights(r):
    auth = json.loads(r.GET["auth"])
    print(222)
    print(auth)
    try:
        print(auth["token"])
        print(type(auth["token"]))
        if auth["id"] != "":
            print(get_auth_token(auth["id"]))
        print((get_auth_token(auth["id"])))
        print(type(get_auth_token(auth["id"])))
        print(auth["token"] == get_auth_token(auth["id"]))
        print(len(auth["token"]))
        print(len( get_auth_token(auth["id"])))
        if auth["id"] != "" and auth["token"] == get_auth_token(auth["id"]):
            user = Users.objects.get(id = auth["id"])
            res =   { "role": user.role, "id": user.id, "name": user.name, "token":
                             create_auth_token(user), "is_blocked_by_admin":user.is_blocked_by_admin,
                "blocked_deadline": user.blocked_deadline}
            print(res)
            return JsonResponse(


             res,
                                content_type="application/json", safe=False, status=200)
        else:
            return  JsonResponse({"role": "", "id": "", "name": "", "token":"", "is_blocked_by_admin": "",
                                  "blocked_deadline":""},
                                content_type="application/json", safe=False, status=200)
    except Exception as e:
        print(e)
        #print("change_role")
        return JsonResponse({"answer": "Немає прав"}, status=400)