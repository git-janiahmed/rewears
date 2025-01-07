from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, View, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Chat, Message, Offer
from userarea.models import Product
from .forms import MessageForm, OfferForm
import pusher
from django.conf import settings
from django.utils import timezone

pusher_client = pusher.Pusher(
    app_id="1829468",
    key="03a7fe18314a890045ed",
    secret="b8f5ca7457a3c3d8f46f",
    cluster="ap2",
    ssl=True,
)


class ChatInboxView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chatapp/chat_inbox.html"
    context_object_name = "chats"

    def get_queryset(self):
        chats = Chat.objects.filter(participants=self.request.user)
        # Attach the unread count to each chat object
        for chat in chats:
            chat.unread_count = chat.unread_messages_count(self.request.user)
        return chats

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_detail.html"
    context_object_name = "chat"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chats = Chat.objects.filter(participants=self.request.user)
        # Attach the unread count to each chat object
        for chat in chats:
            chat.unread_count = chat.unread_messages_count(self.request.user)
        context["chats"] = chats
        context["messages"] = Message.objects.filter(chat=self.object)
        context["offers"] = Offer.objects.filter(chat=self.object)
        context["other_participant"] = self.object.participants.exclude(
            id=self.request.user.id
        ).first()
        context["message_form"] = MessageForm()
        context["offer_form"] = OfferForm()
        context["PUSHER_KEY"] = settings.PUSHER_KEY
        context["PUSHER_CLUSTER"] = settings.PUSHER_CLUSTER

        # Mark all messages as read when the chat is opened
        Message.objects.filter(chat=self.object).exclude(
            sender=self.request.user
        ).update(read=True)

        return context


class CreateOfferView(LoginRequiredMixin, FormView):
    form_class = OfferForm
    template_name = "chatapp/chat_detail.html"

    def form_valid(self, form):
        chat = get_object_or_404(Chat, id=self.kwargs["pk"])
        offer = form.save(commit=False)
        offer.chat = chat
        offer.sender = self.request.user
        offer.receiver = chat.participants.exclude(id=self.request.user.id).first()
        offer.product = chat.product
        offer.save()

        pusher_client.trigger(
            f"chat_{chat.id}",
            "new_offer",
            {
                "description": offer.description,
                "amount": str(offer.amount),
                "sender": offer.sender.username,
                "time": offer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "offer_id": offer.id,
            },
        )

        return redirect(reverse("chat_detail", kwargs={"pk": chat.id}))


class AcceptOfferView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        offer = get_object_or_404(Offer, id=self.kwargs["offer_id"])
        offer.accept()

        return redirect(reverse("chat_detail", kwargs={"pk": offer.chat.id}))


class CancelOfferView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        offer = get_object_or_404(Offer, id=self.kwargs["offer_id"])
        offer.cancel()

        return redirect(reverse("chat_detail", kwargs={"pk": offer.chat.id}))


class CreateChatView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=self.kwargs["product_id"])
        user = request.user

        # Check if a chat already exists for this product between the same users
        existing_chat = Chat.objects.filter(product=product, participants=user).first()

        if existing_chat:
            # Redirect to the existing chat
            return redirect("chat_detail", pk=existing_chat.id)

        # Create a new chat if no existing chat is found
        chat = Chat.objects.create(product=product)
        chat.participants.add(user, product.user)
        chat.save()

        return redirect("chat_detail", pk=chat.id)


class SendMessageView(LoginRequiredMixin, FormView):
    form_class = MessageForm
    template_name = "chatapp/chat_detail.html"

    def form_valid(self, form):
        chat = get_object_or_404(Chat, id=self.kwargs["pk"])
        message = form.save(commit=False)
        message.chat = chat
        message.sender = self.request.user

        message.save()

        message.time = timezone.now()
        message.time = message.time.strftime("%Y-%m-%d %H:%M:%S")
        print(message.time)
        # Trigger a Pusher event
        pusher_client.trigger(
            f"chat_{chat.id}",
            "new_message",
            {
                "message": message.text,
                "sender": message.sender.username,
                "time": message.time,
                "image": message.image.url if message.image else None,
            },
        )

        # Trigger a Pusher event for updating unread count
        for participant in chat.participants.all():
            if participant != self.request.user:
                unread_count = chat.unread_messages_count(participant)
                total_unread_count = chat.total_unread_messages_count(participant)
                print(unread_count)
                pusher_client.trigger(
                    f"user_{participant.id}",
                    "update_unread_count",
                    {
                        "chat_id": chat.id,
                        "unread_count": unread_count,
                        "total_unread_count": total_unread_count,
                    },
                )

        return redirect(reverse("chat_detail", kwargs={"pk": chat.id}))
