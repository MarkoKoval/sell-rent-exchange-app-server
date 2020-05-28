from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from ..notify_email import email_notify
import threading
import time
@csrf_exempt
@transaction.atomic
def change_proposal_blocked(self,id):
    proposal = None
    try:
       proposal =  Proposals.objects.get(id=id)
       proposal.is_blocked_by_admin = not proposal.is_blocked_by_admin
       proposal.save()
    except Exception as e:
        print(e)
        print(333)
        return JsonResponse({},status=400)
    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Ваша пропозиція заблокована '" +proposal.title+ "' для повноцінної робити деталі у   "
                                                               "деталі у адміністратора "
                                                               "надішліть йому повідомлення в платформі чи за поштою johnsmithuk08@gmail.com "
                                                               if
                                                               proposal.is_blocked_by_admin == True else "Ваша пропозиція '" +proposal.title+"'розблокована ",
                                                               proposal.creator_id.email))
    t.setDaemon(True)
    t.start()
  #  t.join(1)
    return JsonResponse({"time":str(time.time())},status=200)
@csrf_exempt
@transaction.atomic
def change_block_status(r, id):
    user = Users.objects.get(id = id)
    user.is_blocked_by_admin = not user.is_blocked_by_admin
    user.save()
    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Ви заблоковані для повноцінної робити деталі у адміністратора "
                                                               "надішліть йому повідомлення в платформі чи за поштою johnsmithuk08@gmail.com " if
                                                               user.is_blocked_by_admin == True else "Ви розблоковані для повноцінної робити ",
                                                               user.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({})
@csrf_exempt
@transaction.atomic
def create_user_complain(r, id):
    try:
        typ = ContentType.objects.get_for_model(Users)
        data = json.loads(r.POST["info"])
        print(data)
        compain = Complaints.objects.create(complain_text=data["text"],
                                            complain_initiator_user_id=data["user_id"],
                                            object_id=id,
                                            content_type=typ)

    except Exception as e:
        print(e)
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)


@csrf_exempt
@transaction.atomic
def create_proposal_complain(r, id):
    try:
        print(2)

        typ = ContentType.objects.get_for_model(Proposals)
        data = json.loads(r.POST["info"])
        print(data)
        compain = Complaints.objects.create(complain_text=data["text"],
                                            complain_initiator_user_id=data["user_id"],
                                            object_id=id,
                                            content_type=typ)

    except Exception as e:
        print(e)
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)


@csrf_exempt
@transaction.atomic
def get_compalain_answer(self, id):
    answer = None
    try:
        answer = ComplaintsAnswers.objects.get(id=id).json()
    except:
        return JsonResponse({}, status=400)
    return JsonResponse({"answer": answer}, status=200)


@csrf_exempt
@transaction.atomic
def delete_complain(r, id):
    try:
        Complaints.objects.get(id=id).delete()
    except:
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)


@csrf_exempt
def get_complains(r, id):
    users = ContentType.objects.get_for_model(Users)
    proposals = ContentType.objects.get_for_model(Proposals)
    """
    typ = ContentType.objects.get_for_model(Complaints)
    data = r.POST["info"]
    p = Proposals.objects.get(id = id)
    compain = Complaints.objects.create(complain_text = data["text"],
                                       complain_initiator_user_id = data["user_id"],
                                       content_type=typ)
    """
    my_complains = [i.json() for i in Complaints.objects.filter(complain_initiator_user=id)]
    to_user = [i.json() for i in Users.objects.get(id=id).coplaints_involved.all()]
    to_proposal = []
    for i in Proposals.objects.filter(creator_id_id=id):  # .coplaints_involved.all()]
        for j in i.coplaints_involved.all():
            to_proposal.append(j.json())
    # proposals(complains)
    my_complains.extend(to_user)
    my_complains.extend(to_proposal)
    print(my_complains)
    return JsonResponse({"result": my_complains})


# /complains/related/
# answer

import threading
@csrf_exempt
@transaction.atomic
def answer_complaint(r, id):
    print(r.POST)
    print(r.POST.keys())
    try:
        data = json.loads(r.POST["info"])
        auth = json.loads(r.POST["auth"])
        print(data)
        #  to_answer =  Complaints.objects.get()
        object_user = Complaints.objects.get(complain_id_id=id).json().object_user
        if data["approve"] == False:
            ComplaintsAnswers.objects.create(complain_id_id=id,
                                             arbiter_id=auth["id"],
                                             approve_complain=data["approve"],

                                             answer_text=data["title"],
                                             )
        u = Users.objects.get(id = object_user.id)

        t = threading.Thread(target=email_notify.send_email, args=( data["title"], "Відповідь на скаргу",u.email))
        t.setDaemon(True)
        t.start()
        t.join(10)


    except Exception as e:
        print(e)
        return JsonResponse({}, status=400)
    return JsonResponse({}, status=200)


# /get/complains/for-desicion/
@csrf_exempt
@transaction.atomic
def complains_for_desicion(r, id):
    result = []
    try:
        proposals = ContentType.objects.get_for_model(Proposals)
        users = ContentType.objects.get_for_model(Users)
        result = []
        users_complains = [i.json() for i in Complaints.objects.filter(~Q(complain_initiator_user=id)
                                                                       & Q(content_type=users) & ~Q(object_id=id))]

        proposals_complains = [i.json() for i in Complaints.objects.filter(~Q(complain_initiator_user=id)
                                                                           & Q(content_type=proposals)
                                                                           )]
        result.extend(users_complains)
        for i in proposals_complains:

            if Proposals.objects.get(id=i["object_id"]).creator_id.id != id:
                result.append(i)
            else:
                continue

        # to_user = [i.json() for i in Users.objects.get(id=id).coplaints_involved.all()]

    # result.extend(proposals_complains)
    except Exception as e:
        print(e)
        return JsonResponse({"result": e}, status=400)

    """
    to_proposal = []
    for i in Proposals.objects.filter(creator_id_id=id):  # .coplaints_involved.all()]
        for j in i.coplaints_involved.all():
            to_proposal.append(j.json())
    """
    # proposals(complains)
    # my_complains.extend(to_user)
    # my_complains.extend(to_proposal)
    # print(my_complains)
    return JsonResponse({"result": result})
    # return JsonResponse({}, status=200)


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
    related = Complaints.objects.filter(complain_initiator_user_id=id)
    return JsonResponse({"result": [i.json() for i in related]}, status=200)



"""
def change_user_blocked(self,id):
    user = None
    try:
       user =  Users.objects.get(id=id)
       user.is_blocked_by_admin = not user.is_blocked_by_admin
       user.save()
    except Exception as e:
        return JsonResponse({},status=400)
    
    return JsonResponse({},status=200)
"""
