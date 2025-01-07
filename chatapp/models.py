from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from orders.models import Order
from userarea.models import Product
from django.urls import reverse_lazy
from userarea.views import send_notification


class Chat(models.Model):
    participants = models.ManyToManyField(User)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="chats")
    created_at = models.DateTimeField(default=timezone.now)

    def unread_messages_count(self, user):
        return self.messages.exclude(sender=user).filter(read=False).count()

    @staticmethod
    def total_unread_messages_count(user):
        return (
            Chat.objects.filter(participants=user)
            .annotate(
                unread_count=models.Count(
                    "messages",
                    filter=models.Q(messages__read=False)
                    & ~models.Q(messages__sender=user),
                )
            )
            .aggregate(total_unread=models.Sum("unread_count"))["total_unread"]
            or 0
        )


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    offer = models.ForeignKey(
        "Offer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )
    accepted = models.BooleanField(default=False)
    image = models.ImageField(
        upload_to="chat_images/", null=True, blank=True
    )  # New field
    read = models.BooleanField(default=False)  # New field to track read status


class Offer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="offers")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="offers"
    )  # Updated reference
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_offers"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="received_offers"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    associated_message = (
        models.OneToOneField(  # Renamed from 'message' to 'associated_message'
            Message,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            related_name="associated_offer",  # Updated related_name
        )
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Offer #{self.id} - {self.amount} AED for {self.product.title}"

    def save(self, *args, **kwargs):
        # Set expiration date if not set (e.g., 24 hours from creation)
        if not self.expires_at and not self.id:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)

        # If this is a new offer being created
        if not self.id:
            super().save(*args, **kwargs)
            # Create associated message
            message = Message.objects.create(
                chat=self.chat,
                sender=self.sender,
                text=f"Offer: {self.amount} AED\n{self.description}",
                offer=self,
            )
            self.associated_message = message

        super().save(*args, **kwargs)

    def accept(self):

        if self.product.status != "reserved":
            """Accept the offer and create an order"""
            if self.status != "pending":
                raise ValueError("Only pending offers can be accepted")

            # Update offer status
            self.status = "accepted"
            self.save()

            # Create order
            order = Order.objects.create(
                buyer=(
                    self.sender if self.sender != self.product.user else self.receiver
                ),
                seller=(
                    self.product.user
                    if self.sender != self.product.user
                    else self.sender
                ),
                product=self.product,
                status="pending",
            )

            # Update product status
            self.product.status = "reserved"
            self.product.save()

            # Send notification to the seller
            seller_message = f"You received a new order from {self.sender if self.sender != self.product.user else self.receiver}"
            seller_link = reverse_lazy("manage_orders")
            send_notification(
                (
                    self.product.user
                    if self.sender != self.product.user
                    else self.sender
                ),
                seller_message,
                notification_type="Order confirmed",
                link=seller_link,
            )
            if self.sender != self.product.user:
                # Send notification to the buyer
                buyer_message = f"Your offer for {self.product.title} has been accepted"
                buyer_link = reverse_lazy("order_list")
                send_notification(
                    self.sender,
                    buyer_message,
                    notification_type="Order confirmed",
                    link=buyer_link,
                )

            # Update message
            if self.associated_message:
                self.associated_message.offer_accepted = True
                self.associated_message.save()

            # Reject all other pending offers for this product
            Offer.objects.filter(product=self.product, status="pending").exclude(
                id=self.id
            ).update(status="rejected")

            return order

    def reject(self):
        """Reject the offer"""
        if self.status != "pending":
            raise ValueError("Only pending offers can be rejected")

        self.status = "rejected"
        self.save()

    def cancel(self):
        """Cancel the offer"""
        if self.status not in ["pending", "accepted"]:
            raise ValueError("Only pending or accepted offers can be cancelled")

        self.status = "cancelled"
        self.save()

        # If there was an order associated with this offer, cancel it
        if self.status == "accepted":
            try:
                order = Order.objects.get(offer=self)
                order.status = "canceled"
                order.save()

                # Update product status back to active
                self.product.status = "active"
                self.product.save()
            except Order.DoesNotExist:
                pass

    @property
    def is_expired(self):
        """Check if the offer has expired"""
        return timezone.now() > self.expires_at if self.expires_at else False

    @property
    def can_be_accepted(self):
        """Check if the offer can be accepted"""
        return (
            self.status == "pending"
            and not self.is_expired
            and not Order.objects.filter(
                product=self.product, status__in=["pending", "confirmed", "shipped"]
            ).exists()
        )
