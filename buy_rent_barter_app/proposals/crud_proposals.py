from ..models import *
#import hashlib
from datetime import datetime
#from django.utils import timezone
from django.db import transaction
from ..system_entrence import system_entrence_
from django.db.models import Q
#from ..notify_email import email_notify
#import threading
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import base64
from django.conf import settings


@csrf_exempt
@transaction.atomic
def add_tags(it, tags):
    print(tags)
    for tag in tags:
        if not it.search_tags.filter(title=tag).exists():
            t, _ = ProposalsTags.objects.get_or_create(title=tag)
            it.search_tags.add(t)
    it.save()


# from .models import Document

from django.core.files.base import ContentFile


def add_wished(it, wished):
    it.wished_items.clear()
    print(wished)
    for w in wished:

        category = None
        try:
            category, _ = ProposalsCategories.objects.get_or_create(category=w["wished_proposal_category"]["category"],
                                                                    subcategory=w["wished_proposal_category"][
                                                                        "subcategory"])
        except Exception as e:
            print(e)
        i, _ = DesiredItemsQueries.objects.get_or_create(category=category,
                                                         query_creator_id=it.creator_id,
                                                         query_description_text=w["wished_description"])
        # print(category.json())
        i.query_description_tags.clear()
        if w["wished_proposal_tags"] != None and len(w["wished_proposal_tags"]) > 0:
            for tags in w["wished_proposal_tags"]:
                t, _ = ProposalsTags.objects.get_or_create(title=tags)
                i.query_description_tags.add(t)
        # print(w.keys())
        res = w["wished_proposal_type"]  # if "wished_proposal_type" in w else w["proposal_item_type"]
        i.proposal_item_type = res
        i.save()
        it.wished_items.add(i)
        # query_description_tags.


import os
import uuid


@csrf_exempt
@transaction.atomic
def add_images(it, images):
    for image in images:
        print(image["path"][:100])

        f, imgstr = image["path"].split(';base64,')
        ext = f.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp' + str(uuid.uuid4()) + "." + ext)
        data = ContentFile(base64.b64decode(imgstr), name='temp' + str(uuid.uuid4()) + "." + ext)
        image = Images.objects.create(path=data, proposal_id=it.id)


@csrf_exempt
def update_images(it, images):
    # print(images.keys())
    ims = []
    for i in images:
        if "url" in i.keys():
            ims.append(i["url"])
    print(ims)
    # print(Images.objects.filter(Q(proposal_id=it.id) & Q(path__url__in = ims )).count())
    # print(Images.objects.filter(Q(proposal_id=it.id).count()))

    for i in Images.objects.filter(Q(proposal_id=it.id)):
        if i.path.url in ims:
            continue
        else:
            i.delete()
            try:
                os.remove(os.path.join(settings.MEDIA_ROOT, i.path.name))
            except:
                pass

    for image in images:

        if "url" in image.keys():
            continue

        else:
            #  print(image.keys())
            #  print(type(image["path"]))
            #  print(image["path"][1:100])
            f, imgstr = image["path"].split(';base64,')
            ext = f.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp' + str(uuid.uuid4()) + "." + ext)
            image = Images.objects.create(path=data, proposal_id=it.id)


#     it.search_tags.add(t)
#  it.save()

# create/proposal
@csrf_exempt
@transaction.atomic
def create(r):
    auth = json.loads(r.POST["auth"])
    # print(auth)
    # print(system_entrence_.get_auth_token(auth["id"]))
    if auth["token"] != system_entrence_.get_auth_token(auth["id"]):
        # print("create")
        return JsonResponse({"answer": "Немає прав або вони змінені пройдіть авторизацію "
                                       "чи перезавантажте сторінку"}, status=400)

    images = json.loads(r.POST["images_"])
    obj = json.loads(r.POST["content"])  # dict(r.POST["content"])

    try:
        p = Proposals.objects.get(title=obj["title"], creator_id_id=obj["creator_id"])
        return JsonResponse({"answer": "Вже є створена пропозиція з таким заголовком"}, content_type="application/json",
                            safe=False, status=400)
    except:
        pass
    # print(obj["available_items"])
    category_, _ = ProposalsCategories.objects.get_or_create(category=obj["category"]["category"],
                                                             subcategory=obj["category"]["subcategory"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    p = Proposals.objects.create(creator_id_id=obj["creator_id"], title=obj["title"], description=obj["description"],
                                 proposal_type=obj["proposal_type"],
                                 proposal_item_type=obj["proposal_item_type"], category=category_,
                                 proposal_item_state=obj["proposal_item_state"],
                                 item_price_value=obj["item_price_value"],
                                 item_price_currency=obj["item_price_currency"],
                                 rent_time_unit_measure=obj["rent_time"],
                                 total_items=obj["available_items"], available_items=obj["available_items"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    print(obj["add_location"])
    if obj["search_tags"]:
        add_tags(p, obj["search_tags"])
    if obj["add_images"] and type(images) == type(list()) and len(images) != 0:
        add_images(p, images)
    # if obj["add_location"]:

    if obj["use_user_location"]:
        u = Users.objects.get(id=obj["creator_id"])
        print(u.location)
        if u.location:
            p.location_id = u.location.id
            p.save()
    elif obj["location"]:
        l = Location.objects.create(lat=obj["location"]["lat"], long=obj["location"]["long"],
                                    str_description=obj["location"]["str_description"])
        p.location_id = l.id
        p.save()
    print(str(obj["proposal_type"]) + " " + str(obj["add_wished"]) + " " + str(obj["wished_items"]))
    if obj["proposal_type"] == "Обмін" and obj["add_wished"] and obj["wished_items"]:
        add_wished(p, obj["wished_items"])
    # [i.json() for i in Proposals.objects.all()]
    return JsonResponse({"proposals": [i.json() for i in Proposals.objects.all()]})


# ,"proposals": [p.json() for p in Proposals.objects.all()] }
# update/proposal
@csrf_exempt
@transaction.atomic
def update(r):
    # print(r.POST.keys())
    # print("update")

    images = json.loads(r.POST["images_"])
    additional = json.loads(r.POST["additional"])
    obj = json.loads(r.POST["content"])
    auth = json.loads(r.POST["auth"])
    # print(auth)
    # print("available_items")
    # print(obj["available_items"])
    # print(system_entrence_.get_auth_token(auth["id"]))
    if auth["token"] != system_entrence_.get_auth_token(auth["id"]):
        print("update")
        return JsonResponse({"answer": "Немає прав або вони змінені пройдіть авторизацію "
                                       "чи перезавантажте сторінку"}, status=400)

    p = Proposals.objects.filter(id=obj["id"])
    pp = Proposals.objects.filter(Q(creator_id_id=obj["creator_id"])
                                  & Q(title=obj["title"]) & ~Q(id=obj["id"])).exists()
    # print(pp)
    if Proposals.objects.filter(Q(creator_id_id=obj["creator_id"])
                                & Q(title=obj["title"]) & ~Q(id=obj["id"])).exists():
        return JsonResponse({"answer": "В вас вже існує  пропозиція з таким заголовком"}, status=400)
    title = obj["title"]
    if p[0].is_in_deal():
        # print(444)
        return JsonResponse({"answer": "Пропозицією хтось вже зацікавився не час редагувати"}, status=400)
    wished_items = json.loads(r.POST["wished_items_"])
    """
    print(wished_items)
    print(obj)
    print(sorted(obj.keys()))

    print(obj["available_items"])
    """
    category_, _ = ProposalsCategories.objects.get_or_create(category=obj["category"]["category"],
                                                             subcategory=obj["category"]["subcategory"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    print(p[0].available_items)
    p.update(creator_id_id=obj["creator_id"], title=obj["title"],
             description=obj["description"],
             proposal_type=obj["proposal_type"],
             proposal_item_type=obj["proposal_item_type"],
             category=category_,
             proposal_item_state=obj["proposal_item_state"],
             item_price_value=obj["item_price_value"],
             item_price_currency=obj["item_price_currency"],
             rent_time_unit_measure=obj["rent_time_unit_measure"],
             total_items=obj["available_items"], available_items=obj["available_items"]),
    # total_items=obj["available_items"], available_items=obj["available_items"]
    print(p[0].available_items)
    p = Proposals.objects.get(id=obj["id"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    # print(134)
    if obj["search_tags"]:
        add_tags(p, obj["search_tags"])
        print(11)
    #   print(str(obj["proposal_type"]) + " " + str(obj["add_wished"]) + " " + str(obj["wished_items"]))
    if obj["proposal_type"] == "Обмін" and additional["change_wished"] and wished_items:
        print(12)
        add_wished(p, wished_items)
    if additional["change_photo"] and type(images) == type(list()) and len(images) != 0:
        print(13)
        update_images(p, images)
        # if additional["change_location"]:
        print(14)
    if additional["use_user_location"]:
        u = Users.objects.get(id=obj["creator_id"])
        if u.location:
            p.location_id = u.location.id
            p.save()
    elif obj["location"]:
        print(15)
        l = Location.objects.create(lat=obj["location"]["lat"], long=obj["location"]["long"],
                                    str_description=obj["location"]["str_description"])
        p.location_id = l.id
        p.save()
    if obj["proposal_type"] == "Оренда" and obj["add_wished"] and obj["wished_items"]:
        print(16)
        add_wished(p, obj["wished_items"])
    # print(p.available_items)
    # print(p.total_items)
    print(11)
    return JsonResponse({"fefew": "ewf"})


def check_categories(cat, category, sup_category):
    # print(cat["category"] == category and cat["subcategory"] == sup_category)
    # print(cat)
    return cat["category"] == category and cat["subcategory"] == sup_category


def check_tags(tags, key_words_):
    return tags is not None and len(list(set(tags).intersection(key_words_))) != 0


def check_price(proposals_, currency, limit, null_set):
    """
    print("sell")
    print(str(currency) + "  " + str(limit))
    print("(proposals_.proposal_type " + str(proposals_.proposal_type))
    print("proposals_.item_price_value " + str(proposals_.item_price_value))
    print("proposals_.item_price_currency " + str(proposals_.item_price_currency))
    print("proposals_.rent_time_unit_measure " + str(proposals_.rent_time_unit_measure))
    print("proposals_.item_price_currency " + str(proposals_.item_price_currency))
    print("proposals_.item_price_value " + str(proposals_.item_price_value))
    """
    if proposals_.proposal_type == "Оренда" and null_set is None:
        print(1)
        return True

    if proposals_.proposal_type == "Обмін":
        print(1)
        return True
    """    
    if proposals_.proposal_type != "Продаж":
        return False
    """
    if proposals_.item_price_value is None:
        print(3)
        return True
    if proposals_.item_price_currency is None:
        print(4)
        return True
    if proposals_.item_price_currency != currency:
        print(5)
        return True
    if (proposals_.item_price_currency == currency and proposals_.item_price_value > limit):
        print(6)
        return True
    print(7)
    return False


def check_rent_price(proposals_, currency, time, limit, null_set):
    print("rent")
    print(str(currency) + " " + str(time) + "  " + str(limit))
    print("(proposals_.proposal_type " + str(proposals_.proposal_type))
    print("proposals_.item_price_value " + str(proposals_.item_price_value))
    print("proposals_.item_price_currency " + str(proposals_.item_price_currency))
    print("proposals_.rent_time_unit_measure " + str(proposals_.rent_time_unit_measure))
    if proposals_.proposal_type == "Продаж" and null_set is None:
        print(1)
        return True
    if proposals_.proposal_type == "Обмін":
        print(1)
        return True
    """
    if proposals_.proposal_type != "Оренда":
        print(2)
        return False
    """

    if proposals_.item_price_value is None:
        print(3)
        return True
    if proposals_.item_price_currency is None:
        print(4)
        return True
    if proposals_.rent_time_unit_measure is None or proposals_.rent_time_unit_measure != time:
        print(5)
        return True
    if proposals_.item_price_currency != currency:
        print(6)
        return True
    if proposals_.item_price_currency == currency and proposals_.item_price_value > limit:
        print(7)
        return True
    print(8)
    return False


# чи доступні
@transaction.atomic
def filter_proposals(proposals_, data):
    print("proposals")
    print(len(proposals_))
    if data["proposal_type"] != "Обмін" and data["price_params"]:
        # print("CHECK CURRENCY")
        if data["price"] and (data["proposal_type"] == "Продаж" or data["proposal_type"] == "Без різниці"):
            # print("CHECK SELL")
            remove = [k for k in proposals_ if
                      check_price(proposals_[k], data["currency"], data["price"], data["rent_price"])]
            for k in remove: del proposals_[k]
        # print("Price " + str(len(proposals_)))
        if data["rent_price"] and (data["proposal_type"] == "Оренда" or data["proposal_type"] == "Без різниці"):
            # print("CHECK RENT")
            remove = [k for k in proposals_ if
                      check_rent_price(proposals_[k], data["rent_currency"], data["rent_time"], data["rent_price"],
                                       data["rent_price"])]
            for k in remove: del proposals_[k]
        # print("Price " + str(len(proposals_)))
        # proposals_ = {k: v for k, v in proposals_.items() if v.proposal_type == "Продаж"}
    if data["proposal_type"] != "Без різниці":
        # print('data["proposal_type"] ' + str(len(proposals_)))
        proposals_ = {k: v for k, v in proposals_.items() if v.proposal_type == data["proposal_type"]}
    # print('data["proposal_type"] ' + str(len(proposals_)))

    if data["proposal_object"] != "Без різниці":
        # print('data["proposal_object"] ' + str(len(proposals_)))
        print(proposals_)
        print(22)
        print(data["proposal_object"])
        print([v.proposal_item_type for k, v in proposals_.items()])
        proposals_ = {k: v for k, v in proposals_.items() if v.proposal_item_type == data["proposal_object"]}
        print(proposals_)
        # print('data["proposal_object"] ' + str(len(proposals_)))

    if data["categories"]:
        # print('data["categories"] ' + str(len(proposals_)))
        #  check_cat = lambda cat,data: cat.category == data["category"] and cat.subcategory == data["sup_category"]
        proposals_ = {k: v for k, v in proposals_.items() if
                      check_categories(v.get_category(), data["category"], data["sup_category"])}
        # print('data["categories"] ' + str(len(proposals_)))

    if data["key_words"]:
        print('data["key_words"] ' + str(len(proposals_)))
        proposals_ = {k: v for k, v in proposals_.items() if check_tags(v.get_tags(), data["key_words_"])}
        print('data["key_words"] ' + str(len(proposals_)))

    print("proposals")
    print(len(proposals_))
    return proposals_


# get/proposals
@transaction.atomic
def get_proposals(r):
    """
    d = []
    for i in d:
        p = PossibleItems.objects.filter(object_id=i)  #.delete()
        req = ProposalsItemsRequests.objects.filter(id=i) #.delete()
        p.delete()
        req.delete()
    """
    # print(r.GET)
    # print(type(r.GET["user_id"]))

    # print(auth["token"])
    # print(system_entrence_.get_auth_token(auth["id"]))

    proposals_ = dict()
    if r.GET and "user_id" in r.GET and r.GET["user_id"] != 'NaN' and r.GET[
        "user_id"] != 0:  # and auth["token"] == system_entrence_.get_auth_token(auth["id"]):

        auth = json.loads(r.GET["auth"])
        #  print(r.GET.keys())
        data = None
        user_id = None
        try:
            data = json.loads(r.GET["query"])
        except:
            pass
        try:
            user_id = r.GET["user_id"]
        except:
            pass
        print(data)
        # print(data == {})
        if data is not None and data != {} and data["title"].strip() != "":
            print(3)
            print("data is not None and data != {} and data['title'].strip() != ")
            t = data["title"].strip()  # data["title"].split()
            # proposals_ = Proposals.objects.filter(title__contains=t )
            print("proposals_")
            for i in t.split():
                if len(i) > 1:
                    # Q(moderated=False)
                    filter_blocked = None
                    print(auth["role"])
                    if auth["role"] == "Адміністратор":
                        filter_blocked = Proposals.objects.filter(
                            Q(title__contains=i) & (Q(total_items=None) | Q(available_items__gte=0)))
                    else:
                        filter_blocked = Proposals.objects.filter(Q(is_blocked_by_admin=False) &
                                                                  Q(title__contains=i) & (Q(total_items=None) | Q(
                            available_items__gte=0)))
                    print(filter_blocked.count())
                    for j in filter_blocked:
                        saved = False
                        if user_id is not None and r.GET["user_id"] != 0:
                            saved = FavoriteProposals.objects.filter(
                                Q(favorite_proposal_id=j.id) & Q(user_id_id=user_id)).exists()
                        if j.id not in proposals_ and not saved:
                            proposals_[j.id] = j

        else:
            print(4)
            # if user_id is not None and r.GET["user_id"] != 0:
            print("f data is None or data == {}")
            filter_blocked = None
            if auth["role"] == "Адміністратор":
                filter_blocked = Proposals.objects.filter(
                    (Q(total_items=None) | Q(available_items__gte=0)))
            else:
                filter_blocked = Proposals.objects.filter(Q(is_blocked_by_admin=False) &
                                                          Q(creator_id__is_blocked_by_admin=False) &
                                                          (Q(total_items=None) | Q(available_items__gte=0)))
            for v in filter_blocked:
                saved = False
                if user_id is not None and r.GET["user_id"] != 0:
                    # print(v.id)
                    #  print(FavoriteProposals.objects.all().values("favorite_proposal_id", "user_id_id"))
                    saved = FavoriteProposals.objects.filter(
                        Q(favorite_proposal_id=v.id) & Q(user_id_id=user_id)).exists()
                # print(saved)
                if not saved:
                    proposals_[v.id] = v

            # print("len " + str(len(proposals_)))

        if data is None or data == {}:
            return JsonResponse({"proposals": [i.json(add_wished_items=False) for i in
                                               proposals_.values()]}, content_type="application/json",
                                safe=False)
        if data is not None and data != {}:
            print(5)
            print("data is not None and data != {}")
            return JsonResponse(
                {"proposals": [i.json(add_wished_items=False) for i in filter_proposals(proposals_, data).values()]},
                content_type="application/json",
                safe=False)

    else:
        data = None

        try:
            data = json.loads(r.GET["query"])
        except:
            pass
        print(data)
        if data is not None and data != {} and data["title"].strip() != "":
            proposals_ = dict()
            print("data is not None and data != {} and data['title'].strip() != ")
            t = data["title"].strip()  # data["title"].split()
            # proposals_ = Proposals.objects.filter(title__contains=t )
            print("proposals_")
            for i in t.split():
                if len(i) > 1:
                    # Q(moderated=False)
                    filter_blocked = Proposals.objects.filter(Q(is_blocked_by_admin=False) &
                                                              Q(title__contains=i) & (Q(total_items=None) | Q(
                        available_items__gte=0)))
                    # print(filter_blocked.count())
                    print("count count count count count count count ")
                    for j in filter_blocked:

                        if j.id not in proposals_:
                            proposals_[j.id] = j

            else:
                filter_blocked = Proposals.objects.filter(Q(is_blocked_by_admin=False) &
                                                          Q(title__contains=i) & (
                                                                  Q(total_items=None) | Q(available_items__gte=0)))
                # print(filter_blocked.count())
                print("count count count count count count count ")
                for j in filter_blocked:

                    if j.id not in proposals_:
                        proposals_[j.id] = j
            print(len(proposals_))
            print("props")
        if data is None or data == {}:
            return JsonResponse({"proposals": [i.json(add_wished_items=False) for i in
                                               Proposals.objects.filter(Q(is_blocked_by_admin=False) & Q(
                                                   creator_id__is_blocked_by_admin=False) & (Q(available_items=None)
                                                                                             | Q(
                                                           available_items__gte=0))
                                                                        )]}, content_type="application/json",
                                safe=False)
        if data is not None and data != {}:

            print("data is not None and data != {}")
            filter_blocked = Proposals.objects.filter(Q(is_blocked_by_admin=False) &
                                                      Q(creator_id__is_blocked_by_admin=False) & (
                                                              Q(total_items=None) | Q(available_items__gte=0)))
            # print(filter_blocked.count())
            print("count count count count count count count ")
            for j in filter_blocked:
                if j.id not in proposals_:
                    proposals_[j.id] = j
            print(len(proposals_))
            return JsonResponse(
                {"proposals": [i.json(add_wished_items=False) for i in filter_proposals(proposals_, data).values()]},
                content_type="application/json",
                safe=False)
    return JsonResponse({"proposals": [i.json(add_wished_items=False) for i in
                                       Proposals.objects.filter(
                                           Q(is_blocked_by_admin=False) & Q(creator_id__is_blocked_by_admin=False) & (
                                                   Q(available_items=None)
                                                   | Q(available_items__gte=0))
                                       )]}, content_type="application/json",
                        safe=False)


# get/requests/to_me/<int:id>
def get_proposal(r, id_):
    return JsonResponse({"proposal": Proposals.objects.get(id=id_).json()})


# proposals/user/<int:id_>
def get_user_proposals(r, id_):
    print("get_user_proposals")
    print(r.GET)
    if "available" in r.GET:
        return JsonResponse({"proposals": [i.json() for i in Proposals.objects.filter(Q(creator_id_id=id_)
                                                                                      & (Q(total_items=None) | ~Q(
            available_items=0)))]})

    return JsonResponse({"proposals": [i.json() for i in Proposals.objects.filter(creator_id_id=id_)]})


# delete/proposals/<int:id_>
@csrf_exempt
@transaction.atomic
def delete_proposals(r, id_):
    auth = None
    try:
        auth = json.loads(r.GET["auth"])
        if auth["token"] == system_entrence_.get_auth_token(auth["id"]) and not Proposals.objects.get(
                id=id_).is_in_deal():
            Proposals.objects.filter(id=id_).delete()
        else:
            return JsonResponse({"result": "Права змінено перезавантажте сторінку або пройдіть"
                                           " авторизацію повторно"}, status=400)
    except:
        JsonResponse({"result": ""}, status=200)

    return JsonResponse({})


# proposals/wished/save/<int:id_>
@csrf_exempt
@transaction.atomic
def save_to_wished(r, id_):
    # print(r.POST)
    try:
        FavoriteProposals.objects.create(favorite_proposal_id_id=id_, user_id_id=r.POST["user_id"])
    except Exception as e:
        # print(e)
        return JsonResponse({"result": e}, status=400)

    return JsonResponse({"result": "Збережено"}, status=200)


# proposals/wished/delete/<int:id_>
@csrf_exempt
@transaction.atomic
def delete_from_wished(r, id_):
    # print(r.GET["user_id"])
    FavoriteProposals.objects.filter(id=id_).delete()
    return JsonResponse({"result": "Видалено"}, status=200)


# proposals/wished/get
@csrf_exempt
def get_wished(r):
    auth = json.loads(r.GET["auth"])
    # print(auth)
    res = None
    try:
        # print(auth["token"])
        print(system_entrence_.get_auth_token(auth["id"]))
        # print(auth["token"] == system_entrence_.get_auth_token(auth["id"]))

        if auth["token"] == system_entrence_.get_auth_token(auth["id"]):
            res = FavoriteProposals.objects.filter(user_id_id=r.GET["user_id"])
        else:
            return JsonResponse({"date": datetime.now(), "result": "Немає прав"}, status=400)

        return JsonResponse({"date": datetime.now(), "result": [i.json() for i in res]}, status=200)
    except:
        return JsonResponse({"date": datetime.now(), "result": [i.json() for i in res]}, status=400)


# proposals/wished_objects/<int:id>'
def wished_proposals_for_exchange_description(r, id):
    wished = Proposals.objects.get(id=id).wished_items.all()
    result = [w.json() for w in wished]

    return JsonResponse({"result": result})


# proposals/get-several
def get_several(r):
    variants_indexes = json.loads(r.GET["proposals"])
    result = []
    # print(variants_indexes)
    for variant in variants_indexes:
        chain = []
        # print(variant)
        for indexes in variant:
            # print(indexes)
            chain.append(Proposals.objects.get(id=indexes).json())

        result.append(chain)
    return JsonResponse({"result": result})
