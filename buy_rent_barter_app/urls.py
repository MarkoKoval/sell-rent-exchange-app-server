from django.urls import path
from .views import *
from .billing_views import *
from .system_entrence import system_entrence_
from .user_profile import user_profile
from .proposals import  crud_proposals
urlpatterns = [
    path("", PayView, name='pay_view'),
    path("users/", user_profile.get_users),
    path("users/<int:id>", user_profile.get_users),
    path("login/", system_entrence_.login),
    path("edit_profile/", user_profile.edit_profile),

    path("get_profile/", user_profile.get_profile),
    path("messages/",user_profile.messages),
    path("delete/messages/<int:id_>", user_profile.delete_messages),
    path("create/proposal", crud_proposals.create),
    path("update/proposal", crud_proposals.update),

    #   path("get/proposals/<int:id_>", crud_proposals.create),
    path("get/proposals", crud_proposals.get_proposals),
    path("get/proposals/<int:id_>", crud_proposals.get_proposal),
    path("proposals/user/<int:id_>", crud_proposals.get_user_proposals),

    path("delete/proposals/<int:id_>", crud_proposals.delete_proposals),

    path("register/", system_entrence_.register),
    path("upload_image/", list1),
    path('pay-callback/', PayCallbackView, name='pay_callback')

]