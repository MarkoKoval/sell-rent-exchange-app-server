from django.urls import path
from .views import *

from .system_entrence import system_entrence_
from .user_profile import user_profile
from .proposals import crud_proposals
from .proposals_requests import proposals_requests
from .donate import donate
#from .complain import complain_handler
from .chain_exchange import chain_exchange
from .complain import complain_handler

urlpatterns = [
    path("donate/<int:id>", donate.PayView, name='pay_view'),
    # path("pay-callback/<int:id>", donate.PayCallbackView),
    path("users/", user_profile.get_users),
    path("users/<int:id>", user_profile.get_users),
    path("login/", system_entrence_.login),
    path("edit_profile/", user_profile.edit_profile),

    path("get_profile/", user_profile.get_profile),
    path("messages/", user_profile.messages),
    path("delete/messages/<int:id_>", user_profile.delete_messages),
    path("create/proposal", crud_proposals.create),
    path("update/proposal", crud_proposals.update),

    #   path("get/proposals/<int:id_>", crud_proposals.create),
    path("get/proposals", crud_proposals.get_proposals),
    path("get/proposals/<int:id_>", crud_proposals.get_proposal),
    path("proposals/user/<int:id_>", crud_proposals.get_user_proposals),

    path("delete/proposals/<int:id_>", crud_proposals.delete_proposals),
    path("proposals/wished/save/<int:id_>", crud_proposals.save_to_wished),
    path("proposals/wished/delete/<int:id_>", crud_proposals.delete_from_wished),
    path("proposals/wished/get", crud_proposals.get_wished),
    path("register/", system_entrence_.register),
    path("upload_image/", list1),
    #  path('pay-callback/', PayCallbackView, name='pay_callback'),

  #  path('create/simple/request/<int:id>', proposals_requests.create_simple_proposal_request),
    path('create/combined/request/<int:id>', proposals_requests.create_combined_proposal_request),

    path('get/requests/to_me/<int:id>', proposals_requests.get_proposal_requests_to_me),
    path('answer/request/<int:id>', proposals_requests.answer_proposal_request_),
    path('get/proposal-requests-details/<int:id>', proposals_requests.get_proposal_request_details),
    path('delete/proposal-request/<int:id>', proposals_requests.delete_proposal_request),
    path('get/my/requests', proposals_requests.get_my_proposal_requests),
    path('create/request/answer/<int:id>', proposals_requests.answer_proposal_request_),
    path('requests/related/me', proposals_requests.me_related_requests),
 #   path('create/complain', complain_handler.create_complain),
    path('find/chain-exchange-variants/<int:id>', chain_exchange.chain_exchange_variants),
    path('proposals/wished_objects/<int:id>', crud_proposals.wished_proposals_for_exchange_description),
    path('proposals/get-several', crud_proposals.get_several),
    path('proposals/approve-object-get/<int:id>',proposals_requests.approve_request_item_get),
    # path('donate',)

    path("proposal/<int:id>/create/complaint",complain_handler.create_proposal_complain),
    path("created/complains/<int:id>",complain_handler.created_complains),
    path("get/complains/<int:id>", complain_handler.get_complains),
    path("delete/complain/<int:id>", complain_handler.delete_complain),
    path("answer/complaint/<int:id>",complain_handler.answer_complaint),
    path("get/complains/for-desicion/<int:id>",complain_handler.complains_for_desicion ),
    path("compalaint/answer/<int:id>",complain_handler.get_compalain_answer),
    path("change/role/user/<int:id>",system_entrence_.change_role ),
    path("get/rights", system_entrence_.get_rights),
    path("user/<int:id>/create/complaint", complain_handler.create_user_complain),
    path("change/block-status/users/<int:id>",complain_handler.change_block_status ),
    path("change/proposal-block-status/proposals/<int:id>", complain_handler.change_proposal_blocked)

    # path("proposal/<int:id>/create/complaint",complain_handler.create_proposal_complain),
   # path("proposal/<int:id>/create/complaint",complain_handler.create_proposal_complain),
    #path(),
   # path()
]
