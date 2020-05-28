from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db import transaction
from ..notify_email import email_notify
import threading

@csrf_exempt
def create_simple_proposal_request(r, id):
    # ProposalsItemsRequests.objects.all().delete()
    # PossibleItems.objects.all().delete()
    print("11111111111111111111111111111111111111111111111111111111111111111111111111111111")
    try:
        print(r.POST)
        user_id = r.POST["user_id"]
        data = json.loads(r.POST["simple"])
        requested_user_id_id = Proposals.objects.get(id=id).creator_id.id
        print(requested_user_id_id)
        print( user_id)
        print(data)
        request = None
        if data["request_deadline_for_answer"] is not None:
            print("CREATE1")
            request = ProposalsItemsRequests.objects.create(
                requested_user_id_id=requested_user_id_id,
                request_user_id_id=user_id,
                request_message=data["request_message"],
                request_deadline_for_answer=parse_datetime(
                    data["request_deadline_for_answer"])
            )
           # return JsonResponse({"result": "success"})
        else:
            print("CREATE2")
            request = ProposalsItemsRequests.objects.create(
                requested_user_id_id=requested_user_id_id,
                request_user_id_id=user_id,
                request_message=data["request_message"])

        if data["request_type"] != "Оренда":
            type = ContentType.objects.get_for_model(ProposalsItemsRequests)
            #  vote, created = Vote.objects.get_or_create(user_voted=user_voted, content_type=type, object_id=object.id
            PossibleItems.objects.create(proposal_item_id_id=id, proposal_item_count=data["proposal_item_count"],
                                         object_id=request.id, content_type=type, proposal=request, type="запит")
        if data["request_type"] == "Оренда":
            type = ContentType.objects.get_for_model(ProposalsItemsRequests)
            # vote, created = Vote.objects.get_or_create(user_voted=user_voted, content_type=type, object_id=object.id
            PossibleItems.objects.create(proposal_item_id_id=id, proposal_item_count=data["proposal_item_count"],
                                         on_rent_time_unit_count=data["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=type,
                                         proposal=request, type="запит")
    except Exception as e:
        return JsonResponse({"result": e})
    """
    print("prop Count")
    print(PossibleItems.objects.count())
    print("REQ Count")
    print(ProposalsItemsRequests.objects.count())
    """
    return JsonResponse({"result": "success"})
    # request_message = []


# /create/combined/request/" + self.$route.params.proposal_id
@csrf_exempt
@transaction.atomic
def create_combined_proposal_request(r, id):
    try:
        print(r.POST)

        data = json.loads(r.POST["data"])
        print(data)
        request = None
        print(222222)
        if data["simple"]["request_deadline_for_answer"] is not None:
            print(request)
            request = ProposalsItemsRequests.objects.create(
                request_main_item = data["simple"]["request_type"],
                requested_user_id_id=Proposals.objects.get(id=id).creator_id.id,
                request_user_id_id=data["user_id"],
                request_message=data["simple"]["request_message"],
                request_deadline_for_answer=parse_datetime(
                    data["simple"]["request_deadline_for_answer"])
            )
        else:
            print(request)
            request = ProposalsItemsRequests.objects.create(
                request_main_item=data["simple"]["request_type"],
                requested_user_id_id=Proposals.objects.get(id=id).creator_id.id,
                request_user_id_id=data["user_id"],
                request_message=data["simple"]["request_message"])

        print(request)

        if data["additional_pay"] is not None and data["additional_pay"]["suggested_money_count"] is not None:
            add = AdditionalRequestsOffers.objects.create(
                suggested_money_count=data["additional_pay"]["suggested_money_count"],
                suggested_currency=data["additional_pay"]["suggested_currency"],
                offer_type=data["additional_pay"]["offer_type"])
            print(33)
            print(add)
            print(44)
            print(add.suggested_money_count)
           # print(add.id)
            print(3555334)
            try:
                request.additional_money_offers =  add
            except Exception as e:
                print(e)
                return JsonResponse({})
            request.save()
        typ = ContentType.objects.get_for_model(ProposalsItemsRequests)
        if data["simple"]["request_type"] == "Продаж" or data["simple"]["request_type"] == "Обмін":
            # type = ContentType.objects.get_for_model(ProposalsItemsRequests)
            #  vote, created = Vote.objects.get_or_create(user_voted=user_voted, content_type=type, object_id=object.id
            PossibleItems.objects.create(proposal_item_id_id=id,
                                         proposal_item_count=data["simple"]["proposal_item_count"],
                                         object_id=request.id, content_type=typ, proposal=request, type="запит")
        if data["simple"]["request_type"] == "Оренда":
            # vote, created = Vote.objects.get_or_create(user_voted=user_voted, content_type=type, object_id=object.id
            PossibleItems.objects.create(proposal_item_id_id=id,
                                         proposal_item_count=data["simple"]["proposal_item_count"],
                                         on_rent_time_unit_count=data["simple"]["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["simple"]["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=typ,
                                         proposal=request, type="запит")
        for it in data["requested_items"]:
            print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["simple"]["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=typ,
                                         proposal=request, type="запит")
        for it in data["suggested_items"]:
            print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["simple"]["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=typ,
                                         proposal=request, type="пропозиція")
    except Exception as e:
        return JsonResponse({"result": e})
    print("prop Count")
    print(PossibleItems.objects.count())
    print("REQ Count")
    print(ProposalsItemsRequests.objects.count())


    creator =    Proposals.objects.get(id=id).creator_id
    t = threading.Thread(target=email_notify.send_email, args=("Новий запит  від користувача "+creator.name, "Деталі на платформі '"+
                                                               data["simple"]["request_message"]+"'", creator.email))
    t.setDaemon(True)
    t.start()
    t.join(10)


    return JsonResponse({"result": "success"})


# get_my_proposal_requests
@csrf_exempt
def get_my_proposal_requests(r):
    # print(PossibleItems.objects.count())
    # p = PossibleItems.objects.filter( Q(content_type__model__startswith="P")

    print(ProposalsItemsRequests.objects.count())
    j = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(request_user_id_id=r.GET["user_id"])]
    print(j)
    print(len(j))
    return JsonResponse({"requests": [i.simple_json() for i in
                                      ProposalsItemsRequests.objects.filter(request_user_id_id=r.GET["user_id"])]})


# pass


# get/requests/to_me/<int:id>'
@csrf_exempt
def get_proposal_requests_to_me(r, id):
    j = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(requested_user_id=id)]
    print(j)
    #  print(len(j))
    return JsonResponse({"requests": j})

import datetime
@csrf_exempt
@transaction.atomic
def approve_requested_object_received(id):
    print("datetime")
    print( datetime.now())
    ProposalsItemsRequests.objects.filter(id = id).update(requested_object_received = datetime.now())
    return JsonResponse({})

@csrf_exempt
@transaction.atomic
def set_waited_for_deal(id):
    ProposalsItemsRequests.objects.get(id = id).items.all().update(waited_for_deal=True)

@csrf_exempt
@transaction.atomic
def answer_proposal_request_(r, id):
    print(12)
    print(r.POST)
    try:
        print(r.POST.keys())
        data = json.loads(r.POST['data'])
        print(data)
        print(data.keys())
        request = None
        print(data["approve"])
        if  data["approve"]  == "Погодження" :
            set_waited_for_deal(id)

        request = ProposalsItemsRequests.objects.create(

            request_user_id_id=data["user_id"], requested_user_id_id=data["answer_to"],
            answered_request_id=id, request_main_item=data["request_main_item"],
            answer_type=data["approve"],
            request_deadline_for_answer=
            parse_datetime(data["request_deadline_for_answer"]) if data[
                "request_deadline_for_answer"]
            else None,
            request_message=data["description"])
        if data["approve"] == "Погодження" or data["approve"] == "Відхилення":

            print(request.request_user_id_id)
            print(request.requested_user_id_id)
            print(request.simple_json())
            print(request.items_json())
            print("ffffff")
            print(request.request_user_id.id)
            print(request.requested_user_id.id)
            if data["approve"] == "Погодження" or data["approve"] == "Відхилення":
                return JsonResponse({})

        if data["additional_pay"] is not None and data["additional_pay"]["suggested_money_count"] is not None:
            add = AdditionalRequestsOffers.objects.create(
                suggested_money_count=data["additional_pay"]["suggested_money_count"],
                suggested_currency=data["additional_pay"]["suggested_currency"],
                offer_type=data["additional_pay"]["offer_type"])
            request.additional_money_offers = add
            request.save()
        type = ContentType.objects.get_for_model(ProposalsItemsRequests)

        for it in data["requested_items"]:
            print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=it["rent_time"],
                                         object_id=request.id, content_type=type,
                                         proposal=request, type="запит")
        for it in data["suggested_items"]:
            print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=it["rent_time"],
                                         object_id=request.id, content_type=type,
                                         proposal=request, type="пропозиція")
    except Exception as e:
        return JsonResponse({"res":e}, status=400)
  #  print("eee")
    creator = Proposals.objects.get(id=id).creator_id
    t = threading.Thread(target=email_notify.send_email, args=("Новий запит від "+creator.name, " Деталі на платформі: '" +
                                                               data["description"]+"'", creator.email))
    t.setDaemon(True)
    t.start()
    t.join(10)
    return JsonResponse({},status=200)



@csrf_exempt
def get_proposal_request_details(r, id):
    # print("wegreger")
    # print(ProposalsItemsRequests.objects.get(id=id).additional_money_offers)
    # print( ProposalsItemsRequests.objects.get(id=id).items.all())
    # res = [i.items_json() for i in ProposalsItemsRequests.objects.get(id=id)]
    return JsonResponse({

                        "request_details":ProposalsItemsRequests.objects.get(id=id).simple_json(),
                        "details": [i.json() for i in ProposalsItemsRequests.objects.get(id=id).items.all()],
                         "request_user_id": ProposalsItemsRequests.objects.get(id=id).request_user_id.id,
                         "additional": None if ProposalsItemsRequests.objects.get(id=id).additional_money_offers is None
                         else ProposalsItemsRequests.objects.get(id=id).additional_money_offers.json()})


# 'delete/proposal-request/<int:id>'
@csrf_exempt
@transaction.atomic
def delete_proposal_request(r, id):
    try:
        ProposalsItemsRequests.objects.filter(id=id).delete()
        """
        answer = ProposalItemsRequestsAnswers.objects.filter(request_id_id=id)
        p = None
        if answer.count() == 0:
            p = ProposalsItemsRequests.objects.filter(id=id)
        elif answer.count() == 1:
            if answer.accept_request:
                return JsonResponse({"requests": "Підтвердити"}, status=400)
            else:
        """
    except:
        return JsonResponse({"requests": {}}, status=400)
    return JsonResponse({"requests": {}}, status=200)

def me_related_requests(r):
    #ProposalsItemsRequests.objects.all().delete()
    user = json.loads(r.GET["user"])
    result = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(Q(request_user_id_id =user["id"]) |
                                                                             Q(requested_user_id_id=user["id"]))]
    print(result)
    return JsonResponse({"requests": result})

from django.utils import timezone
@csrf_exempt
@transaction.atomic
def approve_request_item_get(r, id):
    print(1111)
    print(r.GET)
    print(r.POST)
    r = json.loads(r.POST["params"])
    typ = ContentType.objects.get_for_model(ProposalsItemsRequests)
  #  try:
    if r["answer_type"] == "Пропозиція":
                print(1)
                p = ProposalsItemsRequests.objects.get(id = id)
                print(2)
                p.items.all().filter(Q( content_type=typ) & Q(type="пропозиція")
                                     ).update(accepted_for_deal=True)

                print(3)
                p.requested_object_received = datetime.datetime.now(tz=timezone.utc)
                print(4)
                p.save()
                print(5)
    elif r["answer_type"] == "Погодження":
            print(5)
            p = ProposalsItemsRequests.objects.get(id=r["answered_request"])
            print(6)
            p.items.all().filter(Q(content_type=typ) & Q(type="запит")                 #Q(proposal_item_id_creator_id_id=p.request_user_id_id)
                                 ).update(accepted_for_deal=True)
            print(7)
            p.save()
            print(8)
            approve_request = ProposalsItemsRequests.objects.get(id=id)
            print(9)
            approve_request.requested_object_received = datetime.datetime.now(tz=timezone.utc)
            print(10)
            approve_request.save()
            print(11)

  #  except Exception as e:
   # print(e)
   # print("eeeee")
   # print(e)
    #return JsonResponse({"result": "Виникли труднощі"}, status=400)
    return  JsonResponse({"result": "Підтверджено"}, status=200)