from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from django.utils.timezone import now


class UserProfile(models.Model):

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("O", "other"),
        ("N", "Prefer not to respond"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True)
    verification_code_created = models.DateTimeField(null=True)
    code_regeneration_count = models.IntegerField(default=0)
    photo = models.ImageField(
        upload_to="users_images/", default="users_images/default.webp"
    )
    about = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField(null=True, blank=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    followers_count = models.PositiveIntegerField(default=0)  # New Field
    following_count = models.PositiveIntegerField(default=0)  # New Field

    def generate_verification_code(self):
        # Generate a random 6-digit code
        self.verification_code = "".join([str(random.randint(0, 9)) for _ in range(6)])
        self.verification_code_created = timezone.now()
        self.code_regeneration_count += 1
        self.save()
        return self.verification_code

    def can_regenerate_code(self):
        if self.code_regeneration_count >= 3:
            return False
        if (
            self.verification_code_created
            and timezone.now() - self.verification_code_created < timedelta(minutes=2)
        ):
            return False
        return True

    def __str__(self):
        return f"{self.user.username}'s Profile"
