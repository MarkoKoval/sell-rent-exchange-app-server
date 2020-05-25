from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
@csrf_exempt
@transaction.atomic
def change_role(self,id):
    try:
       user =  Users.objects.get(id=id)
       if user.role == "Звичайний":
           user.role = "Віп"
       elif user.role == "Віп":
           user.role = "Звичайний"
       user.save()
    except Exception as e:
        return JsonResponse({},status=400)
    return JsonResponse({},status=200)