
from ..models import *
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
"""
@csrf_exempt
def find_results(deep, basic_proposal, available):
    results = []
    for obj in available:
        for wished in obj.wished_items.all():
            for basic_wished in basic_proposal.wished_items.all():
                if basic_wished.category.category == wished.category.category and  basic_wished.category.subcategory == wished.category.subcategory:
                    if len(list(set(wished.query_description_tags).intersection(basic_wished.query_description_tags))) > 0:
                        pass


@csrf_exempt
def find_possible_variants(r, id):
    user = r.GET["user"]
    basic_proposal = Proposals.objects.get(id = id)
    available = Proposals.objects.filter(Q(proposal_type = 'Оренда') |  Q(is_blocked_by_admin = False)
                             | ~Q(creator_id = user["id"]) | Q(available_items__gte = 0) |
                                         ~Q(wished_items = None)).v
    deep_count = 3

    return
"""


def comparator(search, wished):
    print("length " + str(search.count()))
    for search_for in search:
        """
        category = search_for.category.category == wished.category.category and \
                   search_for.category.subcategory == wished.category.subcategory
        if not category and search_for.category != "Інше":
            continue
        proposal_type = True if search_for.proposal_item_type == "Нема значення" else\
            search_for.proposal_item_type == wished.proposal_item_type
        if not proposal_type:
            continue
        """

        wished_tags = [i.title.lower() for i in wished.search_tags.all()]
        #print(dir(search_for))
        search_tags = [  i.title.lower() for i in search_for.query_description_tags.all()]
        print("wished: " + str(wished_tags))
        print("searched: " + str(search_tags))

        for  search_tag in search_tags:
            if search_tag in wished_tags:
                print("YES ")

                return True
    #tags = len(list(set([tag.lower() for tag in wished.query_description_tags]).
    #                intersection([tag.lower() for tag in search_for.query_description_tags]))) == 0
    #if tags == 0:
    #    return False
    return False


def simple(id, searched_for,own, possible):
    result = []
   # print("****????????????????????****")
    for i in range(0, len(possible)):
       # print(possible[i].json())
     #   for searched in searched_for:
        if comparator(searched_for, possible[i]) and comparator(possible[i].wished_items.all(),own):
       #     print("JSON " + str(possible[i].json()))
            result.append([id, possible[i].id] )
    print("***!!!!!!!!!!!!!!!!!1********")

    return result


def find_possibille_chain(id, searched_for, own, possible):
    result = []
    a = "ff"
    count = possible.count()
    for i in range(0, count - 1):
        for j in range(i + 1, count):
            if  possible[i].creator_id.id != possible[j].creator_id.id:
                """
                print("******************************************")
                print(own.json())
                print("**********JJJJJJJ*****************")
                print(possible[i].json())
                print("**********JJJJJJJ*****************")
                print(possible[j].json())
                print("******************************************")
                print(str(own.id) +" 1 "+str(possible[i].id))
                """
                first = comparator(searched_for, possible[i])
                """
                print(str(own.id) +" 2 "+str(possible[j].id))
                """
                second = comparator(searched_for, possible[j])

                if  first or second:
                    pass
                else:
                    continue
                #print(str(possible[j].id) + " 3 " + str(possible[i].id))
                third = comparator(possible[j].wished_items.all(), possible[i])
                #print(str(possible[j].id) + " 4 " + str(own.id))
                fourth = comparator(possible[j].wished_items.all(), own)
                if  third or fourth:
                    pass
                else:
                    continue
                #print(str(possible[i].id) + " 5 " + str(possible[j].id))
                fifth = comparator(possible[i].wished_items.all(),possible[j])
                #print(str(possible[i].id) + " 6 " + str(own.id))
                sixth = comparator(possible[i].wished_items.all(),own)
                if  fifth or sixth:
                    pass
                else:
                    continue

                result.append([id, possible[i].id, possible[j].id])
            #    print(str(possible[j].id) + " 3 " + str(possible[i].id))
                """
                if comparator(searched_for, possible[i]) and \
                        comparator(searched_for,possible[j]) \
                        and comparator(possible[j].wished_items.all() , possible[i]):
                    result.append([id , possible[i], possible[j]])
                if comparator(searched_for, possible[j]) and comparator(searched_for,possible[i]) and comparator(
                    possible[i].wished_items.all(),
                    possible[j]):
                    result.append([id, possible[i], possible[j]])
                """
    #     print(result)
    return result

def find_possible_variants(id, user_id):
    own = Proposals.objects.get(id=id)
    searched_for = Proposals.objects.get(id=id).wished_items.all()
    """
    for i in searched_for:
        print(i.json())
    """
  #  own_available = Proposals.objects.filter(Q(proposal_type='Оренда') & Q(is_blocked_by_admin=False)
     #                                    & Q(creator_id=user["id"]) & ( Q(available_items=None) | Q(available_items__gte=0) )&
   #                                      ~Q(wished_items=None))
#    possible = Proposals.objects.filter(Q(proposal_type='Обмін'))
    """
    print(possible.count())
    for i in possible:
        print(i.json())
    """
    possible = Proposals.objects.filter(Q(proposal_type='Обмін') & Q(is_blocked_by_admin=False)
                                         & ~Q(creator_id_id =user_id) & ( Q(available_items=None) | Q(available_items__gte=0) ) &
                                         ~Q(wished_items=None))
    """
    for i in possible:
        print(i.json())
    """
    simple_chain = simple(id,searched_for,own,possible)
    #print(simple_chain)
    multi_chain = find_possibille_chain(id, searched_for, own, possible)
    print(multi_chain)
    result = []
    for i in simple_chain:
        result.append(i)
    for i in multi_chain:
        result.append(i)
    return result
   # print(res)


def chain_exchange_variants(r, id):
    print(r.GET)
    print(1333333333333344)
    user = json.loads(r.GET["user"])
    res = find_possible_variants(id, user["id"])
    """
    for r in res:
        #print("*****")
        for i in r:
            print(str(i) + " "+str(Proposals.objects.get(id = i).json()))
    """
        #print("*****")
   # print(res)
    if len(res) >0 :
        return JsonResponse({"result": res},status=200)
    else:
        return JsonResponse({},status=400)