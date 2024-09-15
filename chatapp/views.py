# views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, View, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message, Offer
from userarea.models import Product
from .forms import MessageForm
import pusher
from django.conf import settings


pusher_client = pusher.Pusher(
    app_id="1829468",
    key="03a7fe18314a890045ed",
    secret="b8f5ca7457a3c3d8f46f",
    cluster="ap2",
    ssl=True,
)


class CreateChatView(LoginRequiredMixin, CreateView):
    model = Chat
    fields = []

    def form_valid(self, form):
        product = get_object_or_404(Product, id=self.kwargs["product_id"])
        chat = Chat.objects.create(product=product)
        chat.participants.add(self.request.user, product.user)
        chat.product = product
        chat.save()
        return redirect("chat_inbox")


class ChatInboxView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chatapp/chat_inbox.html"
    context_object_name = "chats"

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)


class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_detail.html"
    context_object_name = "chat"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chats = Chat.objects.filter(participants=self.request.user)
        context["chats"] = chats
        context["messages"] = Message.objects.filter(chat=self.object)
        context["other_participant"] = self.object.participants.exclude(
            id=self.request.user.id
        ).first()
        context["form"] = MessageForm()
        context["PUSHER_KEY"] = settings.PUSHER_KEY
        context["PUSHER_CLUSTER"] = settings.PUSHER_CLUSTER
        return context


class SendMessageView(LoginRequiredMixin, FormView):
    form_class = MessageForm
    template_name = "chatapp/chat_detail.html"

    def form_valid(self, form):
        chat = get_object_or_404(Chat, id=self.kwargs["pk"])
        message = form.save(commit=False)
        message.chat = chat
        message.sender = self.request.user
        message.save()

        # Trigger a Pusher event
        pusher_client.trigger(
            f"chat_{chat.id}",
            "new_message",
            {"message": message.text, "sender": message.sender.username},
        )

        return redirect(reverse("chat_detail", kwargs={"pk": chat.id}))
