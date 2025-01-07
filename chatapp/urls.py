# urls.py
from django.urls import path, include
from .views import (
    CreateChatView,
    ChatInboxView,
    ChatDetailView,
    SendMessageView,
    CreateOfferView,
    AcceptOfferView,
    CancelOfferView,
)

urlpatterns = [
    path("chat/create/<int:product_id>/", CreateChatView.as_view(), name="create_chat"),
    path("chat/inbox/", ChatInboxView.as_view(), name="chat_inbox"),
    path("chat/<int:pk>/", ChatDetailView.as_view(), name="chat_detail"),
    path("chat/<int:pk>/send/", SendMessageView.as_view(), name="send_message"),
    path("chat/<int:pk>/create_offer/", CreateOfferView.as_view(), name="create_offer"),
    path(
        "offer/<int:offer_id>/accept/", AcceptOfferView.as_view(), name="accept_offer"
    ),
    path(
        "offer/<int:offer_id>/cancel/", CancelOfferView.as_view(), name="cancel_offer"
    ),
]
