from django.urls import path
from .views import *
from .billing_views import *
from .system_entrence import system_entrence_
urlpatterns = [
    path("", PayView, name='pay_view'),
    path("login/", system_entrence_.login),
    path("upload_image/", list1),
    path('pay-callback/', PayCallbackView, name='pay_callback')
]