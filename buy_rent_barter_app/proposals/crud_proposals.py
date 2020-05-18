from ..models import *
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
import hashlib
from datetime import datetime
from django.utils import timezone


@csrf_exempt
def add_tags(it, tags):
    print(tags)
    for tag in tags:
        if not it.search_tags.filter(title=tag).exists():
            t, _ = ProposalsTags.objects.get_or_create(title=tag)
            it.search_tags.add(t)
    it.save()


# from .models import Document
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import base64

from django.core.files.base import ContentFile


def add_wished(it, wished):
    it.wished_items.clear()
    for w in wished:
        print(w.keys())
        print("gerge")
        category = None
        try:
            category, _ = ProposalsCategories.objects.get_or_create(category=w["wished_proposal_category"]["category"],
                                                                subcategory=w["wished_proposal_category"][
                                                                    "subcategory"])
        except Exception as e:
            print(e)
        print("gerge")
        i, _ = DesiredItemsQueries.objects.get_or_create(category = category,
                                                         query_creator_id = it.creator_id,
        query_description_text= w["wished_description"] )
        #i.query_creator_id_id = it.creator_id.id
       # i.query_description_text = w["wished_description"],

        print(category.json())
       # i.category.id = category.id
        i.query_description_tags.clear()
        if  w["wished_proposal_tags"] != None and len(w["wished_proposal_tags"]) > 0:
            for tags in w["wished_proposal_tags"]:
                t, _ = ProposalsTags.objects.get_or_create(title=tags)
                i.query_description_tags.add(t)
        res =  w["wished_proposal_type"] if "wished_proposal_type" in w else w["proposal_item_type"]
        i.proposal_item_type = res
        i.save()
        it.wished_items.add(i)
            #query_description_tags.

import os

import uuid


@csrf_exempt
def add_images(it, images):
    #  print( Images.objects.filter(proposal_id = it.id))
  #  im = Images.objects.filter(proposal_id=it.id)
  #  for i in im:
  #      if os.path.isfile(i.path.path):
  #          os.remove(i.path.path)
  #  im.delete()
    """ 
    img = Images.objects.filter(proposal_id = it.id ).delete()
    for i in img:
        if os.path.isfile(i.path):
            os.remove(i.path)
    """
    for image in images:
        #     for i in Images.objects.filter(proposal_id = it.id):
        # if not Images.objects.filter(proposal_id = it.id, image_hash =  ).exists():
        # t,_ = Images.objects.get_or_create(title=tag)
        print(image.keys())
        f, imgstr = image["path"].split(';base64,')
        ext = f.split('/')[-1]
        data = ContentFile(base64.b64decode(imgstr), name='temp' + str(uuid.uuid4()) + "." + ext)
        image = Images.objects.create(path=data, proposal_id=it.id)


@csrf_exempt
def update_images(it, images):
    for image in images:
        # t,_ = Images.objects.get_or_create(title=tag)
        if image["path"].startswith("temp"):
            continue
        else:
            f, imgstr = image["path"].split(';base64,')
            ext = f.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp' + str(uuid.uuid4()) + "."  + ext)
            image = Images.objects.create(path=data, proposal_id=it.id)


#     it.search_tags.add(t)
#  it.save()

@csrf_exempt
def create(r):
    # return JsonResponse({"images": [i.json() for i in Images.objects.all()]},content_type="application/json", safe=False )
    # serialized_data = serializers.serialize("json", Proposals.objects.all(), ensure_ascii=False)
    # return JsonResponse({"fefew": serialized_data})
    #  print(r.POST)
    # print(r.POST)
    # print(r.POST.keys())
    #  print(r.POST["content"])
    #  print(135)
    # print(type(r.POST["content"]))
    print(43)
    # print(r.POST.keys())
    images = json.loads(r.POST["images_"])

    ## print(images)
    # print(type(images))
    # print(images is None)
    obj = json.loads(r.POST["content"])  # dict(r.POST["content"])
    print(2)
    print(obj)
    # print(j)
    #  print(list(j.keys()))
    # obj = json.loads(list(j.keys())[0])
    #  print(obj)

    try:
        p = Proposals.objects.get(title=obj["title"], creator_id_id=obj["creator_id"])
        return JsonResponse({"result": "Вже є створена пропозиція з таким заголовком"}, content_type="application/json",
                            safe=False, status=400)
    except:
        pass

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
                                 total_items=obj["available_items"],available_items=obj["available_items"] )
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    print(134)
    if obj["search_tags"]:
        add_tags(p, obj["search_tags"])
    if obj["add_images"] and type(images) == type(list()) and len(images) != 0:
        add_images(p, images)
    if obj["add_location"]:
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
    print(str(obj["proposal_type"]) + " "+ str(obj["add_wished"])+ " " + str(obj["wished_items"])      )
    if obj["proposal_type"] == "Обмін" and obj["add_wished"] and obj["wished_items"]:
        add_wished(p, obj["wished_items"])
    # [i.json() for i in Proposals.objects.all()]
    return JsonResponse({"proposals": [i.json() for i in Proposals.objects.all()]})

    # print(12)
    # serialized_data = serializers.serialize("json", Proposals.objects.all(), ensure_ascii=False)
    # return JsonResponse({"fefew": serialized_data})


from django.core import serializers


def cjson(s):
    print(serializers.serialize('json', ProposalsCategories.objects.all(), fields=('id', 'category')))
    return serializers.serialize('json', ProposalsCategories.objects.all(), fields=('id',
                                                                                    'category'))  # list(s.objects.all().values_list("id", "category","subcategory")) #  { "category":s.category,"subcategory":  s.subcategory}


from django.core import serializers

from django.forms.models import model_to_dict


def get(r):
    # print(ProposalsCategories.objects.all().values())

    qs = list(ProposalsCategories.objects.values("id", "category", "subcategory"))

    serialized_data = serializers.serialize("json", Users.objects.all(), ensure_ascii=False)
    print(serialized_data)
    print(type(serialized_data))
    print(type(json.loads(serialized_data)))

    print(json.loads(serialized_data))

    # job = Users.objects.get(pk=1)
    # array_result = serializers.serialize('json', [job], ensure_ascii=False)
    #  print(array_result)
    return JsonResponse(json.dumps(qs, cls=DjangoJSONEncoder), content_type="application/json", safe=False)


# ,"proposals": [p.json() for p in Proposals.objects.all()] }
@csrf_exempt
def update(r):
    print(r.POST.keys())
    print("update")

    images = json.loads(r.POST["images_"])
    additional = json.loads(r.POST["additional"])
    obj = json.loads(r.POST["content"])
    wished_items = json.loads(r.POST["wished_items_"])
    print(wished_items)
    print(obj)
    print(sorted(obj.keys()))
   # p = Proposals.objects.get(title=obj["title"], creator_id_id=obj["creator_id"])

    #  obj = json.loads(list(j.keys())[0])
   # try:
   #     p = Proposals.objects.get(title=obj["title"], creator_id_id=obj["creator_id"])
    #    return JsonResponse({"result": "Вже є створена пропозиція з таким заголовком"}, content_type="application/json",
   #                         safe=False, status=400)
  #  except:
    #    pass
    print(obj["available_items"])
    category_, _ = ProposalsCategories.objects.get_or_create(category=obj["category"]["category"],
                                                             subcategory=obj["category"]["subcategory"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    Proposals.objects.filter(id=obj["id"]).update(creator_id_id=obj["creator_id"], title=obj["title"],
                                                               description=obj["description"],
                                                               proposal_type=obj["proposal_type"],
                                                               proposal_item_type=obj["proposal_item_type"],
                                                               category=category_,
                                                               proposal_item_state=obj["proposal_item_state"],
                                                               item_price_value=obj["item_price_value"],
                                                               item_price_currency=obj["item_price_currency"],
                                                               rent_time_unit_measure=obj["rent_time_unit_measure"],
                                                  available_items=obj["available_items"])
    p = Proposals.objects.get(id=obj["id"])
    # tags  =  ProposalsTags  if obj["search_tags"] else None
    # print(134)
    if obj["search_tags"]:
        add_tags(p, obj["search_tags"])

 #   print(str(obj["proposal_type"]) + " " + str(obj["add_wished"]) + " " + str(obj["wished_items"]))
    if obj["proposal_type"] == "Обмін" and additional["change_wished"] and wished_items:
        add_wished(p, wished_items)
    if additional["change_photo"] and type(images) == type(list()) and len(images) != 0:
        update_images(p, images)
    if additional["change_location"]:
        if additional["use_user_location"]:
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
    if obj["proposal_type"] == "Оренда" and obj["add_wished"] and obj["wished_items"]:
        add_wished(p, obj["wished_items"])

    # print(12)
    return JsonResponse({"fefew": "ewf"})

def check_categories(cat,category,sup_category):
    print(cat["category"] == category and cat["subcategory"] == sup_category)
    print(cat)
    return cat["category"] == category and cat["subcategory"] == sup_category
def check_tags(tags,key_words_):
    return  tags  is not None and len(list(set(tags).intersection(key_words_))) != 0

def check_price(proposals_, currency,limit, null_set):
    print("sell")
    print(str(currency)  + "  "+str(limit))
    print("(proposals_.proposal_type "+str(proposals_.proposal_type))
    print("proposals_.item_price_value " +str(proposals_.item_price_value) )
    print("proposals_.item_price_currency "+str( proposals_.item_price_currency))
    print("proposals_.rent_time_unit_measure " + str(proposals_.rent_time_unit_measure))
    print("proposals_.item_price_currency "+str(proposals_.item_price_currency))
    print("proposals_.item_price_value " + str(proposals_.item_price_value))

    if proposals_.proposal_type == "Оренда" and null_set is None:
        print(1)
        return True

    if proposals_.proposal_type == "Обмін":
        print(1)
        return True
    """    
    if proposals_.proposal_type != "Продаж":
        print(2)
        return False
    """
    if proposals_.item_price_value is None:
        print(3)
        return True
    if proposals_.item_price_currency is None:
        print(4)
        return True
    if  proposals_.item_price_currency != currency:
        print(5)
        return True
    if (proposals_.item_price_currency == currency  and proposals_.item_price_value > limit):
        print(6)
        return True
    print(7)
    return False

def check_rent_price(proposals_, currency,time,limit,null_set ):
    print("rent")
    print(str(currency) +" "+str(time) + "  "+str(limit))
    print("(proposals_.proposal_type "+str(proposals_.proposal_type))
    print("proposals_.item_price_value " +str(proposals_.item_price_value) )
    print("proposals_.item_price_currency "+str( proposals_.item_price_currency))
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
    if  proposals_.rent_time_unit_measure is None or  proposals_.rent_time_unit_measure !=time :
        print(5)
        return True
    if  proposals_.item_price_currency != currency:
        print(6)
        return True
    if  proposals_.item_price_currency == currency  and proposals_.item_price_value > limit:
        print(7)
        return True
    print(8)
    return False

#чи доступні
def filter_proposals(proposals_, data):
    print(data)
    print(13456)
    print(data["proposal_type"])
    print(data["price_params"])
    print(data["price"])
    print(data["proposal_type"])
    print(data["price_params"])
    print(data["price"])
    print(data["rent_price"])

    if data["proposal_type"]  != "Обмін" and data["price_params"]:
        print("CHECK CURRENCY")
        if data["price"] and (data["proposal_type"]  == "Продаж" or data["proposal_type"]  == "Без різниці"):
            print("CHECK SELL")
            remove = [k for k in proposals_ if check_price(proposals_[k],data["currency"] ,data["price"],data["rent_price"]) ]
            for k in remove: del proposals_[k]
            print("Price " + str(len(proposals_)))
        if data["rent_price"] and (data["proposal_type"]  == "Оренда" or data["proposal_type"]  == "Без різниці"):
            print("CHECK RENT")
            remove = [k for k in proposals_ if check_rent_price(proposals_[k],data["rent_currency"] ,data["rent_time"], data["rent_price"],data["rent_price"] )]
            for k in remove: del proposals_[k]
            print("Price "+str(len(proposals_)))
           # proposals_ = {k: v for k, v in proposals_.items() if v.proposal_type == "Продаж"}
    if data["proposal_type"] != "Без різниці":
        print('data["proposal_type"] ' + str(len(proposals_)))
        proposals_ = {k: v for k, v in proposals_.items() if v.proposal_type == data["proposal_type"]}
        print('data["proposal_type"] ' + str(len(proposals_)))
        """
        for i in proposals_.keys():
            if proposals_[i].proposal_type != data["proposal_type"]:
                del proposals_[i]
        """

    if data["proposal_object"] != "Без різниці":
        print('data["proposal_object"] ' + str(len(proposals_)))
        proposals_ = {k: v for k, v in proposals_.items() if v.proposal_item_type == data["proposal_object"]}
        print('data["proposal_object"] ' + str(len(proposals_)))

        """
        for i in proposals_.keys():
            if proposals_[i].proposal_item_type != data["proposal_object"]:
                del proposals_[i]
        """
    if data["categories"]:
        print('data["categories"] ' + str(len(proposals_)))
      #  check_cat = lambda cat,data: cat.category == data["category"] and cat.subcategory == data["sup_category"]
        proposals_ = {k: v for k, v in proposals_.items() if check_categories(v.get_category(),data["category"],data["sup_category"])}
        print('data["categories"] ' + str(len(proposals_)))
        """
        for i in proposals_.keys():
            cat = proposals_[i].proposal_item_type.get_category()
            if cat.category != data["category"] or cat.subcategory != data["sup_category"]:
                del proposals_[i]
        """
    if data["key_words"]:
        print('data["key_words"] ' + str(len(proposals_)))
        proposals_ = {k: v for k, v in proposals_.items() if check_tags(v.get_tags(),data["key_words_"])}
        print('data["key_words"] ' + str(len(proposals_)))
        """
        for i in proposals_.keys():
            tags = proposals_[i].proposal_item_type.get_tags()
            #list(set(tags).intersection(data["key_words_"]))
            if tags is None or len(list(set(tags).intersection(data["key_words_"]))) == 0:
                del proposals_[i]
        """
    print(len(proposals_))
    return proposals_

from django.db.models import Q
def get_proposals(r):
    print(123)
    # if r.method == "GET" and "params" in r.GET.keys():
    #    pass
    """
    serialized_data = serializers.serialize("json", Proposals.objects.all(), ensure_ascii=False)
    print(type(serialized_data))
    print(serialized_data)
    """

    if r.GET:
        print(r.GET.keys())
        data = json.loads(r.GET["query"])
        proposals_ = {}
        if data["title"].strip() != "" :
            t = data["title"].strip() #data["title"].split()
           # proposals_ = Proposals.objects.filter(title__contains=t )
            print("proposals_")
            for i in t.split():
                    if len(i) > 1:
                        # Q(moderated=False)
                        for j in Proposals.objects.filter( Q(title__contains=i) & ( Q(total_items=None)| Q(available_items__gte=0)) ):
                            if  j.id not in proposals_:
                                proposals_[j.id] = j
        else:
            for v in Proposals.objects.all():
                proposals_[v.id] = v
        print(proposals_)
        #filter_proposals(proposals_, data)
        #print(len(proposals_))
        return JsonResponse({"proposals": [i.json() for i in filter_proposals(proposals_, data).values()]}, content_type="application/json",
                                safe=False)

   # filter_proposals(proposals_, data)
   # proposals = {v.id : vfor v in Proposals.objects.all()}
  #  filter_proposals(proposals_, data).values()
    return JsonResponse({"proposals":[i.json() for i in Proposals.objects.all()]}, content_type="application/json", safe=False)


def get_proposal(r, id_):
    """
    serialized_data = serializers.serialize("json", Proposals.objects.filter(id = id_), ensure_ascii=False)
    print(serialized_data)
    return JsonResponse({"proposals": serialized_data}, content_type="application/json", safe=False)
    """
    print()
    return JsonResponse({"proposal": Proposals.objects.get(id=id_).json()})


def delete_proposal(r, id_):
    if r.method == "delete":
        Proposals.objects.filter(id=id_).delete()

    serialized_data = None
    if "creator_id" in r.GET.keys():
        serialized_data = serializers.serialize("json", Proposals.objects.filter(creator_id_id=r.GET["creator_id"]),
                                                ensure_ascii=False)
    return JsonResponse({"proposals": serialized_data}, content_type="application/json", safe=False)


def get_user_proposals(r, id_):
    return JsonResponse({"proposals": [i.json() for i in Proposals.objects.filter(creator_id_id=id_)]})

@csrf_exempt
def delete_proposals(r, id_):
   # Proposals.objects.all().delete()
   # print(24)
    try:
        Proposals.objects.filter(id = id_).delete()
        return JsonResponse({"result": "Видалено"},status=200)
    except Exception as e:
        return JsonResponse({"result": "Не можна видалити"},status=400)