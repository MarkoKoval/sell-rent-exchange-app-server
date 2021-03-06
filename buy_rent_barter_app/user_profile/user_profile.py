from ..models import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from ..system_entrence.system_entrence_ import get_auth_token
from django.db.models import Q
import json
from django.core import serializers


def get_user_info(user):
    obj = None
    try:
        obj = Location.objects.get(id=user.location.id).json()
    except:
        pass

    return {"name": user.name, "email": user.email, "self_description": user.self_description,
            "role": user.role, "location": obj}


# (id_, token)
@csrf_exempt
def edit_profile(request):
    if request.method == "POST":
        try:

            # print(request.POST)
            # print(request.POST.keys())

            id_ = request.POST["id"]
            text = request.POST["description"]
            location = None
            try:
                location = json.loads(request.POST["location"])
            except:
                location = None
            # print(location)
            # print(location.keys() if type(location) == type(dict()) else None)
            # print(location is None)
            # print(type(location))
            #  print(location is not None)
            # print(text)
            # print(location["location"])
            u = Users.objects.get(id=int(id_))
            #  print( u.location)
            u.self_description = text
            if location and u.location is None:
                #  print("location is not None and u.location is None"+location and u.location is None)
                l = Location.objects.create(lat=location["lat"], long=location["long"],
                                            str_description=location["str_description"])
                u.location = l
            elif location:
                #  print("request.POST[location] is not None " + request.POST["location"] is not None)
                Location.objects.filter(id=u.location.id).update(**location)
            u.save()
        except Exception as e:
            # print(e)
            return JsonResponse({"info": e}, content_type="application/json", safe=False, status=400)

        return JsonResponse({"info": "Оновлено"}, content_type="application/json", safe=False, status=200)
    return JsonResponse({"info": "Оновлено"})


import logging

# Get an instance of a logger
import sys
import os

logger = logging.getLogger(__name__)
os.getenv('DJANGO_LOG_LEVEL', 'INFO')


@csrf_exempt
def get_profile(request):
    # print("GET_PROFILE")
    # print(request.GET)
    if request.method == "GET":
        # print("GET_PROFILE")
        # print(request.GET)

        auth = get_auth_token(request.GET["id"])
        # print(request.GET["token"])
        # print(auth)
        # print(request.GET["token"])
        if request.GET["token"] == auth:
            try:

                user = get_object_or_404(Users, id=int(request.GET["id"]))
            except:
                return JsonResponse({"info": "Не вірний запит"}, content_type="application/json", safe=False,
                                    status=404)

            U = get_user_info(user)
            #  print(U)
            return JsonResponse({"info": U},
                                content_type="application/json", safe=False, status=200)
        else:
            return JsonResponse({"info": "Слід авторизуватись"},

                                content_type="application/json", safe=False, status=404)


from django.core.serializers.json import DjangoJSONEncoder
import json


@csrf_exempt
def get_users(request):
    # blog = Users.objects.all().values()
    if request.GET:
        if "except" in request.GET.keys():
            return JsonResponse(
                {"users": [user.json() for user in Users.objects.filter(~Q(id=int(request.GET["except"])))]},
                content_type="application/json", safe=False, status=200)

    return JsonResponse({"users": [user.json() for user in Users.objects.all()]}, content_type="application/json",
                        safe=False, status=200)


# r = list(Users.objects.all().values())
# print(r)
# return JsonResponse({})
# u = Users.objects.all().values_list("name","email","self_description","role","location")
# return JsonResponse({"users":  list(r)}, content_type="application/json", safe=False,status=200)

@csrf_exempt
def messages(r):
    if r.GET:
        #  print(r.GET["sender"])
        #  print(r.GET["receiver"])

        sender = (Q(user_sender_id=(int(r.GET["sender"]))) & Q(user_receiver_id=(int(r.GET["receiver"]))))
        receiver = (Q(user_receiver_id=(int(r.GET["sender"]))) & Q(user_sender_id=(int(r.GET["receiver"]))))

        u = Users.objects.get(id=r.GET["receiver"])
        return JsonResponse(
            {"receiver_name": u.name, "messages": [m.json() for m in UserMessages.objects.filter(sender | receiver)]},
            content_type="application/json", safe=False, status=200)
    if r.POST:
        UserMessages.objects.create(user_receiver_id_id=int(r.POST["receiver"]),
                                    user_sender_id_id=int(r.POST["sender"]),
                                    message_text=(r.POST["message_text"]))
    # print(r.POST)
    #  UserMessages.objects.create(**r.POST)
    return JsonResponse({})


@csrf_exempt
def delete_messages(r, id_):
    UserMessages.objects.filter(id=id_).delete()
    return JsonResponse({})
