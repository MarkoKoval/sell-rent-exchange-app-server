from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db import transaction
from ..notify_email import email_notify
import threading


# /create/combined/request/" + self.$route.params.proposal_id
@csrf_exempt
@transaction.atomic
def create_combined_proposal_request(r, id):
    try:
        # print(r.POST)

        data = json.loads(r.POST["data"])
        # print(data)
        request = None
        if data["simple"]["request_deadline_for_answer"] is not None:
            #  print(request)
            request = ProposalsItemsRequests.objects.create(
                request_main_item=data["simple"]["request_type"],
                requested_user_id_id=Proposals.objects.get(id=id).creator_id.id,
                request_user_id_id=data["user_id"],
                request_message=data["simple"]["request_message"],
                request_deadline_for_answer=parse_datetime(
                    data["simple"]["request_deadline_for_answer"])
            )
        else:
            # print(request)
            request = ProposalsItemsRequests.objects.create(
                request_main_item=data["simple"]["request_type"],
                requested_user_id_id=Proposals.objects.get(id=id).creator_id.id,
                request_user_id_id=data["user_id"],
                request_message=data["simple"]["request_message"])

        # print(request)

        if data["additional_pay"] is not None and data["additional_pay"]["suggested_money_count"] is not None:
            add = AdditionalRequestsOffers.objects.create(
                suggested_money_count=data["additional_pay"]["suggested_money_count"],
                suggested_currency=data["additional_pay"]["suggested_currency"],
                offer_type=data["additional_pay"]["offer_type"])

            # print(add)
            # print(add.suggested_money_count)
            # print(add.id)

            try:
                request.additional_money_offers = add
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
            # print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["simple"]["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=typ,
                                         proposal=request, type="запит")
        for it in data["suggested_items"]:
            # print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=data["simple"]["on_rent_time_unit_measure"],
                                         object_id=request.id, content_type=typ,
                                         proposal=request, type="пропозиція")
    except Exception as e:
        return JsonResponse({"result": e})
    # print("prop Count")
    # print(PossibleItems.objects.count())
    # print("REQ Count")
    # print(ProposalsItemsRequests.objects.count())

    creator = Proposals.objects.get(id=id).creator_id
    t = threading.Thread(target=email_notify.send_email, args=(
        "Новий запит  від користувача " + Users.objects.get(id=data["user_id"]).name, "Деталі на платформі '" +
        data["simple"]["request_message"] + "'", creator.email))
    t.start()

    return JsonResponse({"result": "success"})


# get_my_proposal_requests
@csrf_exempt
def get_my_proposal_requests(r):

    # print(ProposalsItemsRequests.objects.count())
    #j = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(request_user_id_id=r.GET["user_id"])]
    # print(j)
    # print(len(j))
    return JsonResponse({"requests": [i.simple_json() for i in
                                      ProposalsItemsRequests.objects.filter(request_user_id_id=r.GET["user_id"])]})


# pass


# get/requests/to_me/<int:id>'
@csrf_exempt
def get_proposal_requests_to_me(r, id):
    j = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(requested_user_id=id)]
    # print(j)
    #  print(len(j))
    return JsonResponse({"requests": j})


import datetime


@csrf_exempt
@transaction.atomic
def approve_requested_object_received(id):
    # print("datetime")
    # print(datetime.now())
    ProposalsItemsRequests.objects.filter(id=id).update(requested_object_received=datetime.now())
    return JsonResponse({})


@csrf_exempt
@transaction.atomic
def set_waited_for_deal(id):
    ProposalsItemsRequests.objects.get(id=id).items.all().update(waited_for_deal=True)


@csrf_exempt
@transaction.atomic
def set_cencel_for_deal(id):
    if ProposalsItemsRequests.objects.get(id=id).items.all().count() != 0:
        ProposalsItemsRequests.objects.get(id=id).items.all().update(waited_for_deal=False)


@csrf_exempt
@transaction.atomic
def answer_proposal_request_(r, id):
    # print(r.POST)
    request = None
    try:
        # print(r.POST.keys())
        data = json.loads(r.POST['data'])
        # print(data)
        # print(data.keys())

        # print(data["approve"])
        if data["approve"] == "Погодження":
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
            # print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=it["rent_time"],
                                         object_id=request.id, content_type=type,
                                         proposal=request, type="запит")
        for it in data["suggested_items"]:
            # print(it)
            PossibleItems.objects.create(proposal_item_id_id=it["id"],
                                         proposal_item_count=it["count"],
                                         on_rent_time_unit_count=it["on_rent_time_unit_count"],
                                         on_rent_time_unit_measure=it["rent_time"],
                                         object_id=request.id, content_type=type,
                                         proposal=request, type="пропозиція")
    except Exception as e:
        return JsonResponse({"res": e}, status=400)
    # print(request)
    creator = Users.objects.get(id=request.request_user_id_id)  # Proposals.objects.get(id=id).creator_id
    t = threading.Thread(target=email_notify.send_email,
                         args=("Новий запит від " + creator.name, " Деталі на платформі: '" +
                               data["description"] + "'", creator.email))
    t.start()
    return JsonResponse({}, status=200)


@csrf_exempt
def get_proposal_request_details(r, id):
    return JsonResponse({

        "request_details": ProposalsItemsRequests.objects.get(id=id).simple_json(),
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
    except:
        return JsonResponse({"requests": {}}, status=400)
    return JsonResponse({"requests": {}}, status=200)


def me_related_requests(r):
    # ProposalsItemsRequests.objects.all().delete()
    user = json.loads(r.GET["user"])
    # ProposalsItemsRequests.objects.filter(id = 20).delete()
    result = [i.simple_json() for i in ProposalsItemsRequests.objects.filter(Q(request_user_id_id=user["id"]) |
                                                                             Q(requested_user_id_id=user["id"]))]
    # print(result)
    return JsonResponse({"requests": result})


from django.utils import timezone


@csrf_exempt
@transaction.atomic
def approve_request_item_get(r, id):
    # print(r.GET)
    # print(r.POST)
    r = json.loads(r.POST["params"])
    typ = ContentType.objects.get_for_model(ProposalsItemsRequests)
    #  try:
    if r["answer_type"] == "Пропозиція":
        p = ProposalsItemsRequests.objects.get(id=id)
        p.items.all().filter(Q(content_type=typ) & Q(type="пропозиція")
                             ).update(accepted_for_deal=True)
        p.requested_object_received = datetime.datetime.now(tz=timezone.utc)
        p.save()
    elif r["answer_type"] == "Погодження":
        p = ProposalsItemsRequests.objects.get(id=r["answered_request"])
        p.items.all().filter(Q(content_type=typ) & Q(type="запит")
                             # Q(proposal_item_id_creator_id_id=p.request_user_id_id)
                             ).update(accepted_for_deal=True)
        p.save()
        approve_request = ProposalsItemsRequests.objects.get(id=id)
        approve_request.requested_object_received = datetime.datetime.now(tz=timezone.utc)
        approve_request.save()

    return JsonResponse({"result": "Підтверджено"}, status=200)
