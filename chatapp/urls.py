# urls.py
from django.urls import path, include
from .views import CreateChatView, ChatInboxView, ChatDetailView, SendMessageView

urlpatterns = [
    path("chat/create/<int:product_id>/", CreateChatView.as_view(), name="create_chat"),
    path("chat/inbox/", ChatInboxView.as_view(), name="chat_inbox"),
    path("chat/<int:pk>/", ChatDetailView.as_view(), name="chat_detail"),
    path("chat/<int:pk>/send/", SendMessageView.as_view(), name="send_message"),
]
