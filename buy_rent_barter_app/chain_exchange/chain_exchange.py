from ..models import *
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from ..system_entrence import system_entrence_


@csrf_exempt
def comparator(search, wished, compare_name="", initiator=False):

    for search_for in search:

        if initiator:
            # print(search_for.category)
            category = search_for.category.category == wished.category.category and \
                       search_for.category.subcategory == wished.category.subcategory
            if not category and search_for.category.category != "Інше":
                continue

        proposal_type = True if search_for.proposal_item_type == "Нема значення" else \
            search_for.proposal_item_type == wished.proposal_item_type
        if not proposal_type:
            continue

        wished_tags = [i.title.lower() for i in wished.search_tags.all()]
        # print(dir(search_for))
        search_tags = [i.title.lower() for i in search_for.query_description_tags.all()]
        # print(compare_name)
        # print("wished: " + str(wished_tags))
        # print("searched: " + str(search_tags))

        for search_tag in search_tags:
            if search_tag in wished_tags:
                # print("YES ")

                return True

    return False


# формування варіантів ланцюгового обміну з 2 можливих учасників
@csrf_exempt
def simple(id, searched_for, own, possible):
    result = []
    for i in range(0, len(possible)):
        if comparator(searched_for, possible[i]) and comparator(possible[i].wished_items.all(), own):

            result.append([id, possible[i].id])

    return result


@csrf_exempt
def find_possibille_chain(id, searched_for, own, possible):
    result = []

    count = possible.count()
    for i in range(0, count - 1):
        for j in range(i + 1, count):
            if possible[i].creator_id.id != possible[j].creator_id.id:

                # print(possible[i].title + " " + " " + possible[j].title)
                """
                print("******************************************")
                print(own.json())
                print(possible[i].json())
                print(possible[j].json())
                print("******************************************")
                """
                first_second = comparator(searched_for, possible[i], initiator=True)
                first_third = comparator(searched_for, possible[j], initiator=True)
                # print("first_second)  " + str(first_second))
                # print("first_third)  " + str(first_third))
                if first_second or first_third:
                    pass
                else:
                    continue
                third_second = comparator(possible[j].wished_items.all(), possible[i])
                third_first = comparator(possible[j].wished_items.all(), own)
                # print("first_second)  " + str(first_second))
                # print("first_third)  " + str(first_third))
                if third_second or third_first:
                    pass
                else:
                    continue
                second_third = comparator(possible[i].wished_items.all(), possible[j])
                second_first = comparator(possible[i].wished_items.all(), own)
                # print("second_third)  " + str(second_third))
                # print("second_first)  " + str(second_first))
                if second_first or second_third:
                    pass
                else:
                    continue

                # print(possible[i].title + " " + " " + possible[j].title)
                if (first_second and second_third and third_first):
                    result.append([id, possible[i].id, possible[j].id])
                if (first_third and third_second and second_first):
                    result.append([id, possible[j].id, possible[i].id])

    return result


@csrf_exempt
def find_possible_variants(id, user_id):
    own = Proposals.objects.get(id=id)
    searched_for = Proposals.objects.get(id=id).wished_items.all()

    possible =  Proposals.objects.filter(Q(proposal_type='Обмін') & Q(is_blocked_by_admin=False)
                       & ~Q(creator_id_id =user_id) & ( Q(available_items=None) | Q(available_items__gte=0) ) &
                      ~Q(wished_items=None))

    # Proposals.objects.filter(Q(proposal_type='Обмін') & ~Q(
    #    creator_id_id=user_id))

    """
    for i in possible:
        print(i.json())
    """
    # print("SIMPLE")
    simple_chain = simple(id, searched_for, own, possible)
    # print("MULTY")
    # print(simple_chain)
    multi_chain = find_possibille_chain(id, searched_for, own, possible)
    # print(multi_chain)
    result = []
    for i in simple_chain:
        result.append(i)
    for i in multi_chain:
        result.append(i)
    return result


# print(res)

@csrf_exempt
def chain_exchange_variants(r, id):
    auth = json.loads(r.GET["auth"])

    if auth["token"] != system_entrence_.get_auth_token(auth["id"]):
        return JsonResponse(
            {"result": "Права змінились спробуйте перезавантажте сторінку чи пройдіть повторну авторизацію",
             "err": True}, status=400)

    user = json.loads(r.GET["user"])
    res = find_possible_variants(id, user["id"])

    # print(res)
    if len(res) > 0:
        return JsonResponse({"result": res}, status=200)
    else:
        return JsonResponse({}, status=400)
