from .liqp import LiqPay
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from ..models import Users
@csrf_exempt
def PayView(request, id):
        print(11223)
        template_name = 'pay.html'
        name = Users.objects.get(id = id).name
        print(name)

        liqpay = LiqPay("i14834950111", "MOd35a45stEweq6tlDeY83HmPkCGe8nbyCdZ9vEV")
        params = {

            'action': 'paydonate',
            'amount': '1',
            'currency': 'UAH',
            'description': 'Donate від для підтримки платформи '+ name,
            'version': '3',
            'sandbox': 0, # sandbox mode, set to 1 to enable it
            'server_url': '127.0.0.1:8000/pay-callback/', # url to callback view
        }
        signature = liqpay.cnb_signature(params)
        data = liqpay.cnb_data(params)
        print(signature)
        print(data)
        return JsonResponse(json.dumps({'signature': signature, 'data': data}), content_type="application/json", safe=False)
        #return render(request, template_name, {'signature': signature, 'data': data})


