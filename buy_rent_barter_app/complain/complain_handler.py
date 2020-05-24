
from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
@csrf_exempt
@transaction.atomic
def create_proposal_complain(r, id):
    try:
        print(2)
        #print(Complains.objects.count())

        typ = ContentType.objects.get_for_model(Proposals)
        data = json.loads(r.POST["info"])
       # p = Proposals.objects.get(id = id)
        compain = Complaints.objects.create(complain_text = data["text"],
                                           complain_initiator_user_id = data["user_id"],
                                            object_id = id ,
                                           content_type=typ)

    except Exception as e:
        print(e)
        return JsonResponse({},status=400)
    return JsonResponse({},status=200)

@csrf_exempt
def get_complains(r):
    """
    typ = ContentType.objects.get_for_model(Complaints)
    data = r.POST["info"]
    p = Proposals.objects.get(id = id)
    compain = Complaints.objects.create(complain_text = data["text"],
                                       complain_initiator_user_id = data["user_id"],
                                       content_type=typ)
    """
    complains = [i.json() for i in Complaints.objects.all() ]
    return JsonResponse({"created_time": complains})

#/complains/related/

@csrf_exempt
@transaction.atomic
def created_complains(r, id):
    pass
    """
    try:
        typ = ContentType.objects.get_for_model(Complaints)
        data = r.POST["info"]
        p = Proposals.objects.get(id = id)
        compain = Complaints.objects.create(complain_text = data["text"],
                                           complain_initiator_user_id = data["user_id"],
                                            object_id = data["object_id"],
                                           content_type=typ)
    except:
        return JsonResponse({},status=400)
    """
   # related = Complains.objects.filter(complain_initiator_user_id = id )
    #return JsonResponse({"result": [i.json() for i in related]},status=200)

def user_involved_complains(r, id):
    """
    try:
        typ = ContentType.objects.get_for_model(Complaints)
        data = r.POST["info"]
        p = Proposals.objects.get(id = id)
        compain = Complaints.objects.create(complain_text = data["text"],
                                           complain_initiator_user_id = data["user_id"],
                                            object_id = data["object_id"],
                                           content_type=typ)
    except:
        return JsonResponse({},status=400)
    """
   # user = ContentType.objects.get_for_model(Users)
  #  complains = Complains.objects.filter(Q(object_id = id) &
  #                                      Q(content_type = user ))
  #  return JsonResponse({"result": [i.json() for i in complains]},status=200)
    pass
def proposal_involved_complains(r, id):
    """
    try:
        typ = ContentType.objects.get_for_model(Complaints)
        data = r.POST["info"]
        p = Proposals.objects.get(id = id)
        compain = Complaints.objects.create(complain_text = data["text"],
                                           complain_initiator_user_id = data["user_id"],
                                            object_id = data["object_id"],
                                           content_type=typ)
    except:
        return JsonResponse({},status=400)
    """
    #proposals = ContentType.objects.get_for_model(Proposals)
    # complains = Complains.objects.filter(Q(object_id = id) &
                                      #  Q(content_type = proposals))
    # return JsonResponse({"result": [i.json() for i in complains]},status=200)
    pass