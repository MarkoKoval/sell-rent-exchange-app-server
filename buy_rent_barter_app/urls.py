from django.urls import path
from .views import *
from .billing_views import *

urlpatterns = [
    path("", PayView, name='pay_view'),
    path("upload_image/", list1),
    path('pay-callback/', PayCallbackView, name='pay_callback')
]