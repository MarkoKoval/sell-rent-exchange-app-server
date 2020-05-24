from django.db import models

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
import datetime
from django.db.models import Avg, Max, Min, Sum
from django.db import transaction

class Location(models.Model):
    lat = models.FloatField(null=True, blank=True, default=None)
    long = models.FloatField(null=True, blank=True, default=None)
    str_description = models.CharField(default="", max_length=256)

    def json(self):
        return {
            'id': self.id,
            'lat': self.lat,
            'long': self.long,
            'str_description': self.str_description,
        }


# Create your models here.

# користувачі платформи   +
class Users(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, unique=True)
    password_hash = models.CharField(max_length=64, default="")
    email = models.CharField(max_length=100, null=True, blank=True, unique=True)
    self_description = models.TextField(default="Шукаю можливості обміну, продажу, оренди товарів і послуг")
    """
    current_location_lat = models.FloatField(null=True, blank=True, default=None)
    current_location_long = models.FloatField(null=True, blank=True, default=None)
    current_location_str = models.CharField(default="",max_length=256)
    """
    location = models.OneToOneField(Location, on_delete=models.CASCADE, default=None, null=True)
    role = models.CharField(max_length=15, default="Звичайний")  # admin vip
    is_blocked_by_admin = models.BooleanField(default=False)
    time_entered = models.DateTimeField(auto_now_add=True)
    coplaints_involved = GenericRelation("Complaints", related_query_name='complains_to_user', default=None, null=True, blank=True)



    # complains = GenericRelation("Complains")

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "self_description": self.self_description,
            "location": Location.objects.get(id=self.location.id).json() if self.location else None,
            "role": self.role,
            "is_blocked_by_admin": self.is_blocked_by_admin,
            # "complains":  Complains.objects.filter(object_id = self.id).json()
        }

    class Meta:
        ordering = ["name"]


# /users     /users/profiles/<:user_id>


# теги оголошень, що використовуються для їх опису
class ProposalsTags(models.Model):
    title = models.CharField(max_length=256, null=True, blank=True, unique=True)

    class Meta:
        ordering = ["title"]

    def json(self):
        return {"title": self.title}


from django.core.serializers.json import DjangoJSONEncoder
import json
from django.forms import model_to_dict


class ProposalsCategories(models.Model):
    category = models.CharField(max_length=128, null=True, blank=True)
    subcategory = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        ordering = ["category", "subcategory"]
        unique_together = ("category", "subcategory")

    def json(self):
        return {"category": self.category, "subcategory": self.subcategory}


"""
class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
"""


# фото для опису містять хешкоди щоб уникати дублікатів
class Images(models.Model):
    path = models.FileField(upload_to='documents/%Y/%m/%d', default=None)
    proposal = models.ForeignKey("Proposals", on_delete=models.CASCADE, default=None)
    #   uploader_user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    time_uploaded = models.DateTimeField(auto_now_add=True)

    # image_hash = models.CharField(max_length=64, default="")

    class Meta:
        ordering = ["proposal_id", "time_uploaded"]

    def json(self):
        return {"url": self.path.url, "path": self.path.path, "proposal": self.proposal.id}
    #  unique_together = ["uploader_user_id", "image_hash"]


# ProposalsItemsGetConditions
# редагування, видалення оглошення програмно можливе коли немає затверджених запитів купівлі, оренди, обміну
# редагування, видалення програмно неможливе, якщо є назадоволений запит клієнта (непогоджений),
# його можна зробити невидимим для при пошуку
# чи є погодженні запити купівлі, оренди, обміну
# якщо оголошення погодженно можна створити нове оголошення на основі цього яке б ви хотіли редагувати
# і вже його редагувати
# оголошення


class Proposals(models.Model):
    title = models.CharField(max_length=130, default="")
    description = models.TextField(default="")
    category = models.ForeignKey('ProposalsCategories', on_delete=models.CASCADE, default=None)
    search_tags = models.ManyToManyField('ProposalsTags', blank=True, related_name='proposals_tags')
    creation_time = models.DateTimeField(auto_now_add=True)
    creator_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    proposal_type = models.CharField(max_length=8, default="Продаж")  # "SELL"   "RENT" "EXCHANGE"
    proposal_item_type = models.CharField(max_length=8, default="Товари")  # "SERVICES"  "GOODS"
    proposal_item_state = models.CharField(max_length=15, null=True, blank=True)  # "NEW" "USED" # Новий
    location = models.OneToOneField(Location, on_delete=models.CASCADE, default=None, null=True)
    available_items = models.IntegerField(null=True, blank=True, default=None)
    total_items = models.IntegerField(null=True, blank=True, default=None)
    set_visible_for_all = models.BooleanField(default=True)
    is_blocked_by_admin = models.BooleanField(default=False)

    rent_time_unit_measure = models.CharField(max_length=10,
                                              null=True, blank=True)  # "MINUTE","HOUR","DAY","MONTH","YEAR" ЯКЩО ОРЕНДА
    item_price_value = models.FloatField(null=True, blank=True)
    item_price_currency = models.CharField(max_length=10, null=True, blank=True)  # USD EUR default="Гривня"
    wished_items = models.ManyToManyField('DesiredItemsQueries', blank=True, null=True, related_name='desired_items')
    coplaints_involved = GenericRelation("Complaints"    , related_query_name = 'complains_to_proposal', default = None, null = True, blank = True)

    # complains = GenericRelation("Complains")

    class Meta:
        ordering = ["-creation_time"]
        # ordering = ["creator_id", "title"]
        unique_together = ["title", "creator_id"]
    def is_in_deal(self):
        return PossibleItems.objects.filter(Q(proposal_item_id_id=self.id) &
                                     Q(waited_for_deal=True)).exists()


    def get_category(self):
        return ProposalsCategories.objects.get(id=self.category_id).json()

    def get_tags(self):
        return [i.title for i in self.search_tags.all()] if self.search_tags else None

    def simple_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": ProposalsCategories.objects.get(id=self.category_id).json(),
            "search_tags": [i.json() for i in self.search_tags.all()] if self.search_tags else None,
            # Location.objects.get(id=self.location.id).json() if self.location else None,
            "proposal_type": self.proposal_type,
            "proposal_item_type": self.proposal_item_type,
            "proposal_item_state": self.proposal_item_state,
            "location": Location.objects.get(id=self.location.id).json() if self.location else None}

    def get_available(self):
        print("fefwfewfwfwfwef")
        print(PossibleItems.objects.count())
        res = PossibleItems.objects.filter(Q(proposal_item_id_id=self.id) &
                                           Q(accepted_for_deal=True)).aggregate(Sum('proposal_item_count'))
        print(self.total_items)
        print("Available" + str(res))
        if self.total_items != None:
            if res["proposal_item_count__sum"] == None:
                return self.total_items
            else:
                self.available_items =  self.total_items - res["proposal_item_count__sum"]
                self.save()
                return self.available_items
        else:
            return None

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": ProposalsCategories.objects.get(id=self.category_id).json(),
            "search_tags": [i.json() for i in self.search_tags.all()] if self.search_tags else None,
            # Location.objects.get(id=self.location.id).json() if self.location else None,
            "creator_id": self.creator_id.id,
            "proposal_type": self.proposal_type,
            "proposal_item_type": self.proposal_item_type,
            "proposal_item_state": self.proposal_item_state,
            "location": Location.objects.get(id=self.location.id).json() if self.location else None,
            "available_items": self.get_available(),  # self.available_items,
            "total_items": self.total_items,
            "set_visible_for_all": self.set_visible_for_all,
            "is_blocked_by_admin": self.is_blocked_by_admin,
            "rent_time_unit_measure": self.rent_time_unit_measure,
            "item_price_value": self.item_price_value,
            "item_price_currency": self.item_price_currency,
            "images": [i.json() for i in Images.objects.filter(proposal_id=self.id)],
            "wished_items": [i.json() for i in self.wished_items.all()],
            "creation_time": self.creation_time + datetime.timedelta(hours=3)

            #  "wished_items": [i.json() for i in self.search_tags.all()]
            # "complains":  Complains.objects.filter(object_id = self.id).json()
        }


# /advertisements  /advertisements/<:ad_id> /advertisements/users/<:user_id>  /advertisements/goods/<:ad_type>
# /advertisements/goods/<:state>  /advertisements/services/<:ad_type>
# опис бажаних умов продажу для SELL/AUCTION


# опис бажаних умов відданя товару чи послуги
"""
class ProposalsItemsGetConditions(models.Model):
    proposal_id = models.OneToOneField(Proposals, on_delete=models.CASCADE, default=None)
    rent_time_unit_measure = models.CharField(max_length=10,
                                              default="Хвилина")  # "MINUTE","HOUR","DAY","MONTH","YEAR" ЯКЩО ОРЕНДА
    item_price_value = models.FloatField(default=1)
    item_price_currency = models.CharField(max_length=10, default="Гривня")  # USD EUR
    wished_items = models.ManyToManyField('DesiredItemsQueries', blank=True, related_name='desired_items')
    #
"""


#  /advertisements/user/distances/<:user_id>
#  /users/advertisement/distances/<:ad_id>


# збережені оголошення
class FavoriteProposals(models.Model):
    favorite_proposal_id = models.ForeignKey(Proposals, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    added_to_favorite_time = models.DateTimeField(auto_now_add=True)
    visible_for_others = models.BooleanField(
        default=False)  # щоб інші могли запоропонувати це тобі бачачи що ти б це хотів

    class Meta:
        unique_together = ("favorite_proposal_id", "user_id")
        ordering = ["user_id"]

    def json(self):
        return {"id": self.id, "added_to_favorite_time": self.added_to_favorite_time + datetime.timedelta(hours=3),
                "info": Proposals.objects.get(id=self.favorite_proposal_id.id).simple_json()}


# /favorite/users/advertisements/  #/favorite/user/advertisements/<:user_id>

# запит на бажане оголошення що моніторитиметься
class DesiredItemsQueries(models.Model):
    query_creator_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    query_description_text = models.TextField(default="")
    category = models.ForeignKey('ProposalsCategories', on_delete=models.CASCADE, default=None)
    query_description_tags = models.ManyToManyField('ProposalsTags', blank=True,
                                                    related_name='desire_item_description_tags')  # one to many field
    # proposal_type = models.CharField(max_length=15,
    #                                   default="Продаж")  # ("SE", "SELL"), ("RE", "RENT"), ("EX", "EXCHANGE"),("NM", "NO MATTER")
    proposal_item_type = models.CharField(max_length=15,
                                          default="Товари")  # ("GO", "GOODS"),("SE", "SERVICE"),("NM", "NO MATTER")
    # proposal_item_state = models.CharField(max_length=15, null=True, blank=True)  # ("N", "NEW"),("U", "USED"),("NM", "NO_MATTER")
    query_creation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    visible_for_others = models.BooleanField(default=False)

    def json(self):
        return {
            "query_creator_id": self.query_creator_id.id,
            "query_description_text": self.query_description_text,
            "category": self.category.json(),
            "query_description_tags": [i.json() for i in self.query_description_tags.all()],
            "proposal_item_type": self.proposal_item_type,
            "query_creation_time": self.query_creation_time,
            "is_active": self.is_active,
            "visible_for_others": self.visible_for_others
        }

    # щоб інші могли запоропонувати це тобі бачачи що ти б це хотів видно якщо віп


# users/desired/advertisements  users/desired/advertisements/<:user_id>
# users/desired/sell/advertisements users/desired/sell/advertisements/<:category_type>
# users/desired/sell/advertisements/<:category_type>


# теги для опису бажаного товару чи послуги
"""
class DesiredItemsDescriptionTags(models.Model):
    title = models.CharField(max_length=256, unique=True, null=True, blank=True)

    class Meta:
        ordering = ["title"]
"""

# повідомлення від системи про наявність бажаного обєкта за критерыями описаного в оголошенні
"""
class DesiredItemExistenceNotifications(models.Model):
    query_id = models.ForeignKey(DesiredItemsQueries, on_delete=models.CASCADE,default=None)
    proposal_id = models.ForeignKey(Proposals, on_delete=models.CASCADE,default=None)
    notification_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["query_id"]
"""


#   users/desired/advertisements/notifications/<:user_id>


class AdditionalRequestsOffers(models.Model):
    #   description = models.TextField(default="")
    suggested_money_count = models.FloatField(default=1)
    suggested_currency = models.CharField(max_length=10, default="Гривня")
    offer_type = models.CharField(max_length=25,
                                  default="Хотів би отримати")  # "WANT GIVE" "WANT RECEIVE" "Хотів би надати"

    def json(self):
        return {"id": self.id, "suggested_money_count": self.suggested_money_count,
                "suggested_currency": self.suggested_currency, "offer_type": self.offer_type}


#  class Meta:
#      ordering = ["suggested_currency"]
from django.db.models import Q


class PossibleItems(models.Model):
    on_rent_time_unit_measure = models.CharField(max_length=10, null=True, blank=True,
                                                 default=None)  # ("MINUTE"),("HOUR"),("DAY"),("MONTH"),("YEAR") якщо потрібно
    on_rent_time_unit_count = models.IntegerField(null=True, blank=True, default=None)
    proposal_item_count = models.IntegerField(null=True, blank=True, default=None)
    proposal_item_id = models.ForeignKey(Proposals, on_delete=models.CASCADE)
    waited_for_deal = models.BooleanField(default=False)
    accepted_for_deal = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None)
    object_id = models.PositiveIntegerField(default=None)
    proposal = GenericForeignKey('content_type', 'object_id')
    type = models.CharField(default="запит", max_length=10)  # suggest пропозиція

    def json(self):
        return {
            "type": self.type,
            "id": self.id, "on_rent_time_unit_measure": self.on_rent_time_unit_measure,
            "on_rent_time_unit_count": self.on_rent_time_unit_count,
            "proposal_item_count": self.proposal_item_count,
            "proposal_item_id": self.proposal_item_id.id,
            "waited_for_deal": self.waited_for_deal, "accepted_for_deal": self.accepted_for_deal,
            "proposal_description": Proposals.objects.get(id=self.proposal_item_id_id).simple_json()}


class ProposalsItemsRequests(models.Model):
    request_user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    requested_user_id = models.ForeignKey(Users, on_delete=models.CASCADE, default=None, null=True, blank=True,
                                          related_name="requested_user")
    request_main_item = models.CharField(max_length=20, default="Продаж")  # Sell Exchange Rent №ЗАБРАТИ
    request_message = models.TextField(default="")
    # type = models.CharField(default="Простий", max_length=15)  # комбінований
    items = GenericRelation(PossibleItems, related_query_name='queried_items', default=None, null=True, blank=True)
    # requested_items = GenericRelation(
    #     "PossibleItems")  # models.ManyToManyField('PossibleItems', related_name='requested_items')  # робити перевірку чи дані
    #  suggested_items = GenericRelation("PossibleItems",
    #                                   blank=True)  # models.ManyToManyField('PossibleItems', blank=True,
    #     related_name='suggested_items')  # елементи вже не використані
    additional_money_offers = models.OneToOneField(AdditionalRequestsOffers, on_delete=models.CASCADE, default=None,
                                                   null=True, blank=True)

    request_time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    request_deadline_for_answer = models.DateTimeField(default=None, null=True, blank=True)
    #  total_accept_approve_answer = models.DateTimeField(default=None, null=True, blank=True)
    requested_object_received = models.DateTimeField(default=None, null=True, blank=True)  # чи виконане за реквастом
    answered_request = models.ForeignKey("ProposalsItemsRequests", on_delete=models.CASCADE, default=None, null=True,
                                         blank=True)
    answer_type = models.CharField(default="Пропозиція", max_length=15)  # Відхилити Запропонувати

    # review = GenericRelation('Reviews')

    def get_main_proposal(self):
        p = PossibleItems.objects.filter(Q(object_id=self.id) & Q(content_type__model__startswith="P")
                                         & Q(type="request"))
        print(' PPPPPP')
        #   print(p[0].proposal_item_id_id)
        #    print(p)
        print(None if len(p) == 0 else p[0].proposal_item_id.json())
        return None if len(p) == 0 else p[0].proposal_item_id_id
    """
    def answer_(self):
        p = ProposalItemsRequestsAnswers.objects.filter(request_id_id=self.id)

        return None if p.count() == 0 else p[0].json()
    """
    @transaction.atomic
    def approve_request_item_get(self):
        try:
            self.requested_object_received = datetime.datetime.now()
            self.save()
            self.items.all().filter(proposal_item_id_creator_id_id = self.request_user_id_id).update(accepted_for_deal=True)
        except Exception as e:
            print(e)
    def answered(self):
        try:
            return ProposalsItemsRequests.objects.get(answered_request_id=self.id).id
        except:
            return None

    def reanswer_for_request_proposal(self):
        p = ProposalsItemsRequests.objects.filter(answered_request_id=self.id)
        count = p.count()
        return None if count == 0 else p[count-1].answer_type
    def reanswer_wish(self):
        p = ProposalsItemsRequests.objects.filter(answered_request_id=self.id)
        count = p.count()
        return None if count == 0 else p[count-1].request_main_item
    def simple_json(self):
        return {"id": self.id, "request_user_id": self.request_user_id.id if self.request_user_id else None,
                "requested_user_id": self.requested_user_id.id if self.requested_user_id else None,
                "main_item": self.items.all().count(),
                "answered": self.answered(),
                "author": self.request_user_id.name,
                "answer_user": self.requested_user_id.name,
                "request_main_item": self.request_main_item, "answer": "", # self.answer_(),
                "requested_main_item": self.items.all()[
                    0].proposal_item_id.id if self.items.all().count() != 0 else None,  # self.get_main_proposal(),
                "request_message": self.request_message,  # "type": self.type,
                "request_time": self.request_time + datetime.timedelta(hours=3),
                "request_deadline_for_answer": self.request_deadline_for_answer,
                "answer_type": self.answer_type,
                "title": self.items.all().filter(
                    type="запит").first().proposal_item_id.title if self.items.all().count() != 0 else None,  ###
                # "total_accept_approve_answer": self.total_accept_approve_answer,
                "requested_object_received": self.requested_object_received,
                "answered_request": self.answered_request.id if self.answered_request else None,
                "reanswer_for_request_proposal": self.reanswer_for_request_proposal(),
                "reanswer_wish": self.reanswer_wish()
                }

    def items_json(self):
        return {"res": [i.json() for i in self.items.all()]}

    class Meta:
        ordering = ["-request_time"]


# скасовується якщо вийшов дедлайн для людей показує доступна менша кількість поки дедлайн існує для схвалення при резервації

# gen
# запропоновані гроші для оренди


# відповідь можливому покупцю на запит купівлі
"""
class ProposalItemsRequestsAnswers(models.Model):
    request_id = models.OneToOneField(ProposalsItemsRequests, on_delete=models.CASCADE)
    accept_request = models.BooleanField(default=True)
    answer_message = models.TextField(default="")
    answer_time = models.DateTimeField(auto_now_add=True)
    wished_items = GenericRelation(
        "PossibleItems")  # models.ManyToManyField('PossibleItems', blank=True, related_name="wished_items_")
    additional_money_offers = models.ForeignKey(AdditionalRequestsOffers, on_delete=models.CASCADE, default=None)
    back_answer_deadline = models.DateTimeField(default=None)
    #   accepted_time_by_requested_user = models.DateTimeField(default=None) # той хто швидше погодить якщо морочить голову робиться запит до адміна щоб обмежив його дії
    confirm_requested_object_give_action = models.DateTimeField(default=None)

    def wished(self):
        w = self.wished_items.all()
        return None if len(w) == 0 else [i.json() for i in w]

    def json(self):
        return {"id": self.request_id_id, "accept_request": self.accept_request,
                'answer_message': self.answer_message, 'answer_time': self.answer_time, "wished_items": self.wished,
                # self.wished_items.all(),
                'additional_money_offers': self.additional_money_offers,
                'back_answer_deadline': self.back_answer_deadline,
                'confirm_requested_object_give_action': self.confirm_requested_object_give_action}
"""

#   users/requests/buy/answers/<:buy_request_id> users/requests/buy/answers/


#   згенерований можливий ланцюговий обмін  ДУМАЙ потім додаються сюди
"""
class PossibleChainExchangeProposals(models.Model):
    chain_exchange_id = models.IntegerField()
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    chain_exchange_proposal_items = GenericRelation(
        PossibleItems)  # models.ManyToManyField('PossibleItems', blank=True,
    #                   related_name="items_for_chain_exchange")  # елементи які пропонуються для обміну
    additional_money_offers = models.ForeignKey(AdditionalRequestsOffers, on_delete=models.CASCADE, default=None)
    proposal_message = models.TextField(default="")
    creation_time = models.DateTimeField(auto_now_add=True)
    reject_proposal_at_all = models.DateTimeField(default=None)
    exchange_approve = models.DateTimeField(default=None)
"""

# review = GenericRelation('Reviews')


"""
class Wishes(models.Model): #ProposalItemsRequestsAnswers
    wanted_items = models.ManyToManyField('PossibleItems', blank=True, related_name='wanted_items_')
    additional_money_offers = models.ForeignKey(AdditionalRequestsOffers,on_delete=models.CASCADE , default=None)
    approve_deadline_for_previous = models.DateTimeField(default=None)
    approve_accepted = models.DateTimeField(default=None)
"""

"""
class ChainExchangeProposalsAnswers(models.Model):
    chain_exchange_block_id = models.OneToOneField(PossibleChainExchangeProposals, on_delete=models.CASCADE)
    accept_exchange_conditions = models.BooleanField(default=True)
    wished_items = GenericRelation("PossibleItems",
                                   blank=True)  # models.ManyToManyField('PossibleItems', blank=True, related_name="items_for_chain_exchange")
    additional_money_offers = models.ForeignKey(AdditionalRequestsOffers, on_delete=models.CASCADE, default=None)

    answer_message = models.TextField(default="")  # відповідь на запропоновані речі для обміну
    answer_time = models.DateTimeField(auto_now_add=True)
    back_deadline_answer = models.DateTimeField(default=None)
"""

# gen

# gen

"""
class Reviews(models.Model):
    reviewer_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    # review_object_type = models.CharField(max_length=15, default="Продаж") #exchange "chain exchange" "rent" "sell"
    #  review_object = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None)  #
    #  object_id = models.PositiveIntegerField(default=None)
    #  content_object = GenericForeignKey('review_object', 'object_id')
    reviewed_simple_proposal = models.ForeignKey(Proposals, on_delete=models.CASCADE, default=None, null=True,
                                                 blank=True)
    reviewed_chain_proposal = models.ForeignKey(PossibleChainExchangeProposals, on_delete=models.CASCADE, default=None,
                                                null=True, blank=True)
    review_text = models.TextField(default="")
    review_mark = models.CharField(max_length=10, default="добре")  # погано задовільно відмінно
    review_time = models.DateTimeField(auto_now_add=True)
"""


##gen
# request = GenericForeignKey("request_answer_id")

class UserMessages(models.Model):
    message_text = models.TextField(default="")
    user_sender_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_sender_id', default=None)
    user_receiver_id = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_receiver_id', default=None)
    time_send = models.DateTimeField(auto_now_add=True)

    def json(self):
        return {
            "id": self.id,
            "message_text": self.message_text,
            "user_sender_id": self.user_sender_id.id,
            "user_receiver_id": self.user_receiver_id.id,
            "time_send": self.time_send,
        }


# request = GenericForeignKey("topic_id")

# gen

class ComplaintsAnswers(models.Model):
    complain_id = models.OneToOneField("Complaints", on_delete=models.CASCADE)
    arbiter = models.ForeignKey(Users, on_delete=models.CASCADE)
    answer_text = models.TextField(default="Ок таке рішення")
    sanction = models.CharField(max_length=30, default="Без санкцій")  # "BLOCK ACCOUNT", "BLOCK SPECIFIED CONTENT",
    # "BLOCK ACCOUNT AND BLOCK SPECIFIED CONTENT", "NO SANCTIONS","BAD COMPLAIN")
    approve_complain = models.BooleanField(default=False)
    sanction_deadline = models.DateTimeField(default=None)
    answer_time = models.DateTimeField(auto_now_add=True)

    def json(self):
        return {"complain_id": self.complain_id,
                "arbiter": {"name": self.arbiter.name, "id": self.arbiter.id},
                "sanction": self.sanction,
                "answer_text": self.answer_text,
                "approve_complain": self.approve_complain,
                "sanction_deadline": self.sanction_deadline,
                "answer_time": self.answer_time
                }

    class Meta:
        ordering = ["-answer_time"]

class Complaints(models.Model):
   # topic_type = models.CharField(max_length=30,
   #                               default="Поганий контент")  # "BAD CONTENT","SELL","RENT","EXCHANGE","CHAIN_EXCHANGE"

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, default=None)
    object_id = models.PositiveIntegerField(default=None)
    complain_object = GenericForeignKey('content_type', 'object_id')
    complain_text = models.TextField(default="Поганий контент")
    complain_initiator_user = models.ForeignKey(Users, related_name='initiator_user', on_delete=models.CASCADE,
                                                default=None,
                                                blank=True, null=True)
    created_time = models.DateTimeField(auto_now_add=True)
    def get_answer(self):
        try:

           answer = ComplaintsAnswers.objects.get(complain_id_id = self.id)
           return answer.json()
        except Exception as e:
            return None

    def json(self):
        return  {
            "complain_text": self.complain_text,
            "complain_initiator_user": self.complain_initiator_user.name,
            "created_time": self.created_time,
            "content_type": str(self.content_type),
            "answer": self.get_answer()
       #     "complain_object": self.content_type
        }
    class Meta:
        ordering = ["-created_time"]




#   описати платежі
"""
class Donations(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    donation_time = models.DateTimeField(auto_now_add=True)
    donation_message = models.TextField(default="")
    donation_value = models.FloatField(default=1)
    donation_currency = models.CharField(max_length=3, default="Гривня")

"""

# class SanctionsByAdmins(models.Model): # санкції за неправомірну поведінку адміном
# зробити узгодження виставлення оцінок


from django.db import models

# Create your models here.
"""
class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
"""
