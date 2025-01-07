from django.db import models
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Category(models.Model):
    name = models.CharField(max_length=100)
    
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    icon_img = models.ImageField(upload_to="category_icons/", null=True, blank=True)


    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="brands"
    )

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sizes"
    )

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("draft", "Draft"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    condition = models.CharField(max_length=50)
    colors = models.ManyToManyField(Color)
    material = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    upload_time = models.DateTimeField(auto_now_add=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, null=True)
    brand_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="product_images/")

    def __str__(self):
        return f"Image for {self.product.title}"


from django.conf import settings


class Wishlist(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "user",
            "product",
        )  # Ensures a product is added to a user's wishlist only once

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Follow(models.Model):
    follower = models.ForeignKey(
        UserProfile, related_name="following", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        UserProfile, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower", "following"]),
        ]

    def __str__(self):
        return f"{self.follower.user.username} follows {self.following.user.username}"


@receiver(post_save, sender=Follow)
def update_follow_counts_on_create(sender, instance, created, **kwargs):
    if created:
        follower_profile = instance.follower
        following_profile = instance.following

        UserProfile.objects.filter(pk=follower_profile.pk).update(
            following_count=models.F("following_count") + 1
        )
        UserProfile.objects.filter(pk=following_profile.pk).update(
            followers_count=models.F("followers_count") + 1
        )


@receiver(post_delete, sender=Follow)
def update_follow_counts_on_delete(sender, instance, **kwargs):
    follower_profile = instance.follower
    following_profile = instance.following

    UserProfile.objects.filter(pk=follower_profile.pk).update(
        following_count=models.F("following_count") - 1
    )
    UserProfile.objects.filter(pk=following_profile.pk).update(
        followers_count=models.F("followers_count") - 1
    )


from django.utils.timezone import now


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("FOLLOW", "Followed User's Activity"),
        ("ORDER", "Order Activity"),
        ("GENERAL", "General Notifications"),
    ]
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(default=now)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def mark_as_read(self):
        self.is_read = True
        self.save()

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"
