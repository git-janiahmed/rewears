from django.db import models
from tinymce.models import HTMLField


class HelpCenterTopic(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()  # TinyMCE field
    icon = models.ImageField(upload_to="help_icons/")

    def __str__(self):
        return self.title


class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=200, default="Privacy Policy")
    content = HTMLField()  # TinyMCE field
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class TermsAndConditions(models.Model):
    title = models.CharField(max_length=200, default="Terms and Conditions")
    content = HTMLField()  # TinyMCE field
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject


class Update(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()  # TinyMCE field
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
