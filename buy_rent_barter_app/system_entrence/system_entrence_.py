#from ..models import Users
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def login(request):
    if request.method == "POST":
        print(request.POST)
        print(len(request.POST))
    return JsonResponse(json.dumps({"response": "200"}), content_type="application/json", safe=False)


def register(request):
    pass