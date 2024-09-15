from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from userarea.models import Product


class Chat(models.Model):
    participants = models.ManyToManyField(User)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="chats"
    )
    created_at = models.DateTimeField(default=timezone.now)


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    offer = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    accepted = models.BooleanField(default=False)


class Offer(models.Model):
    chat = models.ForeignKey(Chat, related_name="offers", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
