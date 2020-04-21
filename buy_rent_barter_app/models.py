from django.db import models

from django.db import models
#from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.

# користувачі платформи   +
class Users(models.Model):
    user_name = models.CharField(max_length=64, unique=True)
    user_password_hash = models.CharField(max_length=77, default="")  # Хешування паролю аргон2
    user_email = models.CharField(max_length=64, null=True, blank=True, unique=True)
    user_description = models.TextField(default="")
    user_current_location_lat = models.FloatField(default=None)
    user_current_location_long = models.FloatField(default=None)
    user_last_time_visited = models.DateTimeField(auto_now_add=True)

    user_vip_status = models.BooleanField(default=False)
    user_admin_status = models.BooleanField(default=False)
    show_user_profile_for_all = models.BooleanField(default=True)

    class Meta:
        ordering = ["user_name"]

# /users     /users/profiles/<:user_id>


# соціальні мережі користувача для додаткового звязку  +
class UsersSocialNetworks:
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    social_network_link = models.CharField(max_length=128, unique=True)
    social_network_name = models.CharField(max_length=15, null=True, blank=True, unique=True)

    class Meta:
        ordering = ["user_id"]


# теги оголошень, що використовуються для їх опису
class AdvertisementsTags(models.Model):
    ad_tag = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["ad_tag"]


# фото для опису містять хешкоди щоб уникати дублікатів
class Images(models.Model):
    img_path = models.CharField(max_length=256)
    uploader_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    img_time_uploaded = models.DateTimeField(auto_now_add=True)
    img_hashcode = models.CharField(max_length=77, default="")

    class Meta:
        ordering = ["uploader_id", "img_time_uploaded"]


# редагування, видалення оглошення програмно можливе коли немає затверджених запитів купівлі, оренди, обміну
# редагування, видалення програмно неможливе, якщо є назадоволений запит клієнта (непогоджений),
# його можна зробити невидимим для при пошуку
# чи є погодженні запити купівлі, оренди, обміну
# якщо оголошення погодженно можна створити нове оголошення на основі цього яке б ви хотіли редагувати
# і вже його редагувати
# оголошення
class Advertisements(models.Model):
    ad_name = models.CharField(max_length=256)
    ad_description_text = models.TextField()
    ad_description_images = models.ManyToManyField('Images', blank=True, related_name='ad_description_images')
    ad_search_tags = models.ManyToManyField('AdvertisementsTags', blank=True, related_name='advertisements_tags')
    ad_creation_time = models.DateTimeField(auto_now_add=True)

    ad_creator_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    AD_TYPE = (
        ("SE", "SELL"),
        ("RE", "RENT"),
        ("EX", "EXCHANGE"),
    )

    ad_type = models.CharField(max_length=2, choices=AD_TYPE, default="SE")
    AD_ITEM_TYPE = (
        ("GO", "GOODS"),
        ("SE", "SERVICES")
    )

    ad_item_type = models.CharField(max_length=2, choices=AD_ITEM_TYPE, default="GO")
    AD_ITEM_STATE = (
        ("NE", "NEW"),
        ("US", "USED")
    )
    ad_item_state = models.CharField(max_length=2, choices=AD_ITEM_STATE, default="NE")

    ad_location_latitude = models.FloatField(default=None)
    ad_location_longitude = models.FloatField(default=None)

    available_items = models.IntegerField(default=1)
    total_items = models.IntegerField(default=1)
    set_email_notification = models.BooleanField(default=True)
    set_visible_for_all = models.BooleanField(default=True)
    ad_item_description_content_hashcode = models.CharField(max_length=77, default="")  # хешкод даних оголошення для уникнення несанкціонованої зміни інформації оголошення

    class Meta:
        ordering = ["ad_creator_id", "ad_name"]

# /advertisements  /advertisements/<:ad_id> /advertisements/users/<:user_id>  /advertisements/goods/<:ad_type>
# /advertisements/goods/<:state>  /advertisements/services/<:ad_type>
# опис бажаних умов продажу для SELL/AUCTION


class AdvertisementsItemsPrices(models.Model):
    ad_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)
    ad_item_price_value = models.FloatField(default=0.0)
    ad_item_price_currency = models.CharField(max_length=20, default="UAH")
    price_set_time = models.DateTimeField(auto_now_add=True)


# опис бажаних умов оренди
class AdvertisementsItemsRentConditions(models.Model):
    ad_id = models.OneToOneField(Advertisements, on_delete=models.CASCADE,  unique=True)

    TIME_MEASURES = (
        ("M", "MINUTE"),
        ("H", "HOUR"),
        ("D", "DAY"),
        ("M", "MONTH"),
        ("Y", "YEAR")
    )
    suggested_rent_time_unit_measure = models.CharField(max_length=1, choices=TIME_MEASURES, default="D")
    suggested_ad_item_price_value = models.FloatField(default=1)
    suggested_ad_item_price_currency = models.CharField(max_length=20, default="UAH")
    wished_ad_items = models.ManyToManyField('DesiredAdsItemsQueries', blank=True, related_name='desired_items')
    rent_conditions_set_time = models.DateTimeField(auto_now_add=True)
    #


# опис бажаних умов для обміну
class AdvertisementsItemsExchangeConditions(models.Model):
    ad_id = models.OneToOneField(Advertisements, on_delete=models.CASCADE, unique=True)
    suggested_ad_item_price_value = models.FloatField(default=0.0) # якщо потрібна грошова доплатаpy
    suggested_ad_item_price_currency = models.CharField(max_length=20, default="UAH")
    wished_ad_items = models.ManyToManyField('DesiredAdsItemsQueries', blank=True, related_name='wished_items_for_exchange')
    exchange_conditions_set_time = models.DateTimeField(auto_now_add=True)


# дистанції між  користувачем і місця оголощень якщо їхні локації встановлені
class UsersAdvertisementsLocationsDistances(models.Model):
    ad_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    distance_in_km = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("ad_id", "user_id")
        ordering = ["user_id"]

#  /advertisements/user/distances/<:user_id>
#  /users/advertisement/distances/<:ad_id>


# збережені оголошення
class FavoriteAdvertisements(models.Model):
    favorite_ad_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    added_to_favorite_time = models.DateTimeField(auto_now_add=True)
    description_text = models.CharField(max_length=512, default="")
    visible_for_others = models.BooleanField(default=True) #   щоб інші могли запоропонувати це тобі бачачи що ти б це хотів

    class Meta:
        unique_together = ("favorite_ad_id", "user_id")
        ordering = ["user_id"]

# /favorite/users/advertisements/  #/favorite/user/advertisements/<:user_id>


# запит на бажане оголошення що моніторитиметься
class DesiredAdsItemsQueries(models.Model):
    query_creator_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    query_description_text = models.TextField(default="Would like this")
    query_description_tags = models.ManyToManyField('DesiredItemsDescriptionTags', blank=True,
                                                    related_name='desire_item_description_tags')
    query_ad_category_type = (
        ("SE", "SELL"),
        ("RE", "RENT"),
        ("BA", "BARTER"),
        ("NM", "NO MATTER")
    )
    ad_type = models.CharField(max_length=2, choices=query_ad_category_type, default="NM")

    query_ad_item_category_type = (
        ("GO", "GOODS"),
        ("SE", "SERVICE"),
        ("NM", "NO MATTER")
    )
    ad_item_type = models.CharField(max_length=1, choices=query_ad_item_category_type, default="NM")
    query_ad_item_state = (
        ("N", "NEW"),
        ("U", "USED"),
        ("NM", "NO_MATTER")
    )
    ad_item_state = models.CharField(max_length=2, choices=query_ad_item_state, default="NM")
    notify_on_email = models.BooleanField(default=True)
    query_creation_time = models.DateTimeField(auto_now_add=True)
    visible_for_others = models.BooleanField(default=True)  #щоб інші могли запоропонувати це тобі бачачи що ти б це хотів

# users/desired/advertisements  users/desired/advertisements/<:user_id>
# users/desired/sell/advertisements users/desired/sell/advertisements/<:category_type>
# users/desired/sell/advertisements/<:category_type>


# теги для опису бажаного товару чи послуги
class DesiredItemsDescriptionTags(models.Model):
    desired_item_description_tag = models.CharField(max_length=128, unique=True)

    class Meta:
        ordering = ["desired_item_description_tag"]


# повідомлення про наявність бажаного обєкта за критерыями описаного в оголошенні
class DesiredItemExistenceNotifications(models.Model):
    query_for_desired_ads_item_id = models.ForeignKey(DesiredAdsItemsQueries, on_delete=models.CASCADE)
    suggested_item_ad_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)
    notification_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["query_for_desired_ads_item_id"]

#   users/desired/advertisements/notifications/<:user_id>


# запит на купівлю обєкта оголошення якщо якісь непорозуміння звертання до адміна
class BuyRequests(models.Model):
    possible_buyer_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    request_ad_item_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)
    request_message = models.CharField(max_length=1024, default="some text")
    requested_ad_item_count = models.IntegerField(default=1)
    request_time = models.DateTimeField(auto_now_add=True)
    request_seller_watched = models.DateTimeField(default=None)
    request_deadline_for_seller_answer = models.DateTimeField(default=None)
    buy_approve = models.DateTimeField(default=None) #чи виконане за реквастом
    notify_on_email = models.BooleanField(default=True)
    buy_proposal_hashcode = models.CharField(max_length=77, default="") # ad_item_description_content_hashcode + count

    class Meta:
        ordering = ["possible_buyer_id", "request_ad_item_id"]

#   users/requests/buy/<:user_id> users/requests/buy


# відповідь можливому покупцю на запит купівлі
class AdsItemBuyRequestAnswer(models.Model):
    buy_request_id = models.ForeignKey(BuyRequests, on_delete=models.CASCADE)
    accept_request = models.BooleanField(default=True)
    answer_message = models.CharField(max_length=1024, default="please contact me for further info")
    answer_time = models.DateTimeField(auto_now_add=True)
    answer_buyer_watched = models.DateTimeField(default=None)
    approve_deadline_for_buyer = models.DateTimeField(default=None)
    approve_by_buyer_accepted_time = models.DateTimeField(default=None) # той хто швидше погодить якщо морочить голову робиться запит до адміна щоб обмежив його дії
    cell_approve = models.DateTimeField(default=None)
#   users/requests/buy/answers/<:buy_request_id> users/requests/buy/answers/


# запит на оренду
class RentRequests(models.Model):
    possible_renter_id = models.ForeignKey(Users, on_delete=models.CASCADE)

    request_message = models.TextField()

    requested_ad_items = models.ManyToManyField('PossibleRentItems', related_name='requested_rent_items') # робити перевірку чи дані
    suggested_ad_items = models.ManyToManyField('PossibleRentItems', blank=True, related_name='suggested_rent_items') # елементи вже не використані
    request_time = models.DateTimeField(auto_now_add=True)
    request_watched_time = models.DateTimeField(default=None) #  rentgiver чи побачив запит
    request_deadline_for_answer = models.DateTimeField(default=None) # deadline для відповіді
    rent_approve = models.DateTimeField(default=None)
    notify_on_email = models.BooleanField(default=True)
    requested_items_info_hashcode = models.CharField(max_length=77, default="") # d_item_description_content_hashcode + count
#   users/requests/rent/<:user_id> users/requests/rent


class PossibleRentItems(models.Model):
    TIME_MEASURES = (
        ("M", "MINUTE"),
        ("H", "HOUR"),
        ("D", "DAY"),
        ("M", "MONTH"),
        ("Y", "YEAR")
    )
    suggested_rent_time_unit_measure = models.CharField(max_length=1, choices=TIME_MEASURES, default="D")
    suggested_rent_time_unit_count = models.IntegerField(default=1)
    ad_item_count = models.IntegerField(default=1)
    ad_item_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("suggested_rent_time_unit_measure", "suggested_rent_time_unit_count", "ad_item_count", "ad_item_id")


# запропоновані гроші для оренди
class RentRequestPriceOffers(models.Model):
    rent_request = models.OneToOneField(RentRequests, on_delete=models.CASCADE, unique=True)
    suggested_price = models.FloatField(default=1)
    suggested_currency = models.CharField(max_length=10, default="UAH")
    TYPE_OF_OFFER = (
        ("WG", "WANT GIVE"),
        ("WR", "WANT RECEIVE")
    )
    offer_type = models.CharField(max_length=2, choices=TYPE_OF_OFFER , default="WG")


# відповідь орендодавця на запит оренди
class AdsItemsRentRequestsAnswers(models.Model):
    rent_request = models.ForeignKey(RentRequests, on_delete=models.CASCADE)
    accept_request = models.BooleanField(default=True)
    answer_message = models.TextField( default="please contact me for further info")
    answer_time = models.DateTimeField(auto_now_add=True)
    answer_renter_watched = models.DateTimeField(default=None)
    approve_deadline_for_renter = models.DateTimeField(default=None)
    approve_by_renter_accepted = models.DateTimeField(default=None)  #забє і все зробити можливість одразу відмовитись
    rent_approve = models.DateTimeField(default=None)
#   users/requests/rent/answers/<:rent_request_id> users/requests/rent/answers/


#   запит на обмін
class ExchangeRequests(models.Model):
    exchange_initiator = models.ForeignKey(Users, on_delete=models.CASCADE)
    requested_ad_items = models.ManyToManyField('PossibleExchangeItems', related_name='desired_items_for_exchange')
    suggested_ad_items = models.ManyToManyField('PossibleExchangeItems', blank=True, related_name='suggested_items_for_exchange')
    request_message = models.TextField(default="some text")
    request_time = models.DateTimeField(auto_now_add=True)
    request_watched = models.DateTimeField(default=None)
    request_deadline_to_answer = models.DateTimeField(default=None)
    exchange_approve = models.DateTimeField(default=None)
    notify_on_email = models.BooleanField(default=True)
    requested_items_info_hashcode = models.CharField(max_length=77, default="")  # d_item_description_content_hashcode + count


class PossibleExchangeItems(models.Model):
    ad_item_count = models.IntegerField(default=1)
    ad_item_id = models.ForeignKey(Advertisements, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("ad_item_count", "ad_item_id")


# запропоновані гроші для оренди
class ExchangeRequestsPriceOffers(models.Model):
    EXCHANGE_TYPE = (
        ("SE", "SIMPLE EXCHANGE"),
        ("CE", "CHAIN EXCHANGE")
    )
    exchange_type = models.CharField(max_length=2, choices=EXCHANGE_TYPE , default="WG")
    rent_request = models.ForeignKey( ContentType, on_delete=models.CASCADE)
    suggested_price = models.FloatField(default=1)
    suggested_currency = models.CharField(max_length=10, default="UAH")
    TYPE_OF_OFFER = (
        ("WG", "WANT GIVE"),
        ("WR", "WANT RECEIVE")
    )
    offer_type = models.CharField(max_length=1, choices= TYPE_OF_OFFER , default="WG")
    offer_time = models.DateTimeField(auto_now_add=True)
    offer_watched = models.DateTimeField(default=None)
    deadline_for_offer_answer = models.DateTimeField(default=None)


#   відповідь на запит на обмін
class AdsItemExchangeRequestsAnswers(models.Model):
    rent_request_id = models.ForeignKey(ExchangeRequests, on_delete=models.CASCADE)
    accept_request = models.BooleanField(default=True)
    answer_message = models.CharField(max_length=1024, default="please contact me for further info")
    answer_time = models.DateTimeField(auto_now_add=True)
    answer_watched = models.DateTimeField(default=None)
    approve_deadline = models.DateTimeField(default=None)
    approve_accepted_time = models.DateTimeField(default=None)
    rent_approve = models.DateTimeField(default=None)
    suggested_items_info_hashcode = models.CharField(max_length=77, default="")


#   згенерований можливий ланцюговий обмін  ДУМАЙ
class PossibleChainExchange(models.Model):
    chain_id = models.IntegerField()
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    chain_exchange_proposal_items = models.ManyToManyField('PossibleExchangeItems', blank=True, related_name="ads_items_for_chain_exchange") #елементи які пропонуються для обміну
    creation_time = models.DateTimeField(auto_now_add=True)
    previous_suggested_items_info_hashcode = models.CharField(max_length=77, default="")  # argon2
    exchange_approve = models.DateTimeField(default=None)
    notify_on_email = models.BooleanField(default=True)


class ChainExchangeParticipantsAnswers(models.Model):
    chain_exchange_block_id = models.ForeignKey(PossibleChainExchange, on_delete=models.CASCADE)
    accept_exchange_conditions = models.BooleanField(default=True)
    answer_message = models.TextField( default="please contact me for further info") # відповідь на запропоновані речі для обміну
    answer_time = models.DateTimeField(auto_now_add=True)
    answer_next_chain_exchanger_watched = models.DateTimeField(default=None)
    answer_deadline_for_next_chain_exchanger = models.DateTimeField(default=None)


class ChainExchangeWishes(models.Model):
    chain_exchange_answer = models.ForeignKey(ChainExchangeParticipantsAnswers, on_delete=models.CASCADE)
    wanted_items_for_chain_exchange = models.ManyToManyField('PossibleExchangeItems', blank=True, related_name='wanted_items_for_chain_exchange')
    answer_message = models.TextField( default="please contact me for further info")
    answer_time = models.DateTimeField(auto_now_add=True)
    answer_watched = models.DateTimeField(default=None)
    approve_deadline_for_previous = models.DateTimeField(default=None)
    approve_accepted = models.DateTimeField(default=None)


class AdItemBuyRentExchangeOnFinishingRankings(models.Model):
    request_answer_id = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # AdsItemBuyRequestAnswer
    reviewer_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    review_text = models.TextField()
    review_ranking = models.FloatField(default=0.0)
    review_time = models.DateTimeField(auto_now_add=True)
    review_description_images = models.ManyToManyField('Images', blank=True, related_name='review_images')


# request = GenericForeignKey("request_answer_id")
class UserMessages(models.Model):
    message_text = models.TextField()
    message_sender_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    time_send = models.DateTimeField(auto_now_add=True)
    message_edited = models.BooleanField(default=False)
    MESSAGE_FOR_TOPIC = (
        ("CO", "Complain"),
        ("SE", "SELL"),
        ("RE", "RENT"),
        ("BA", "BARTER"),
        ("CE", "CHAIN_EXCHANGE")
    )
    topic_type = models.CharField(max_length=2, choices=MESSAGE_FOR_TOPIC, default="SE")
    topic_id = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    description_images = models.ManyToManyField('Images', blank=True, related_name='description_images')

    class Meta:
        ordering = ["topic_type", "topic_id", "time_send"]


# request = GenericForeignKey("topic_id")


class Complains(models.Model):
    Complain_FOR_TOPIC = (
        ("BC", "BAD CONTENT"),
        ("SE", "SELL"),
        ("RE", "RENT"),
        ("EX", "EXCHANGE"),
        ("CE", "CHAIN_EXCHANGE")
    )
    topic_type = models.CharField(max_length=2, choices=Complain_FOR_TOPIC, default="SE")
    topic_id = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    complain_description_text = models.TextField()
    complain_initiator_user = models.ForeignKey(Users,related_name='complain_initiator_user', on_delete=models.CASCADE)
    complain_subject_user = models.ForeignKey(Users, related_name="complain_subject_user", on_delete=models.CASCADE)
    complain_time = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["topic_type"]


class ComplainAnswers(models.Model):
    complain_id = models.ForeignKey(Complains, on_delete=models.CASCADE)
    arbiter_to_resolve = models.ForeignKey(Users, on_delete=models.CASCADE)
    arbiter_verdict = models.TextField()
    sanction_types = ( ("BA", "BLOCK ACCOUNT"), ("BSC", "BLOCK SPECIFIED CONTENT"),
                      ("BADSC", "BLOCK ACCOUNT AND BLOCK SPECIFIED CONTENT"), ("NS", "NO SANCTIONS"),
                       ("BC", "BAD COMPLAIN") )
    sanction = models.CharField(max_length=5, choices=sanction_types, default="NS")
    approve_complain = models.BooleanField(default=False)
    sanction_time_available = models.DateTimeField(default=None)
    answer_time = models.DateTimeField(auto_now_add=True)


#   описати платежі
class Donations(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    donation_time = models.DateTimeField(auto_now_add=True)
    donation_message = models.TextField(default="")
    donation_value = models.FloatField(default=1)
    donation_currency = models.CharField(max_length=10, default="UAH")

#class SanctionsByAdmins(models.Model): # санкції за неправомірну поведінку адміном
# зробити узгодження виставлення оцінок