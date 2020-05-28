from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q
from ..notify_email import email_notify
import threading
@csrf_exempt
@transaction.atomic
def change_role(self,id):
    user = None
    try:
       user =  Users.objects.get(id=id)
       if user.role == "Звичайний":
           user.role = "Віп"
       elif user.role == "Віп":
           user.role = "Звичайний"
       user.save()
    except Exception as e:
        return JsonResponse({},status=400)

    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Зміна ролі коричтувача на "+user.role , user.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({},status=200)

def change_blocked(self,id):
    user = None
    try:
       user =  Users.objects.get(id=id)
       user.is_blocked_by_admin = not user.is_blocked_by_admin
       user.save()
    except Exception as e:
        return JsonResponse({},status=400)
    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Ви заблоковані для повноцінної робити деталі у адміністратора  " if
                                                               user.is_blocked_by_admin == True else    "Ви розблоковані для повноцінної робити ", user.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({},status=200)

def change_proposal_blocked(self,id):
    proposal = None
    try:
       proposal =  Proposals.objects.get(id=id)
       proposal.is_blocked_by_admin = not proposal.is_blocked_by_admin
       proposal.save()
    except Exception as e:
        return JsonResponse({},status=400)
    t = threading.Thread(target=email_notify.send_email, args=("Повідомлення від платформи пропозицій продажу "
                                                               "оренди обміну товарів і послуг ",
                                                               "Ваша пропозиція заблокована '" +proposal.title+ "' для повноцінної робити деталі у адміністратора  " if
                                                               proposal.is_blocked_by_admin == True else "Ваша пропозиція '" +proposal.title+"'розблокована ",
                                                               proposal.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({},status=200)