from django.db import models
from tinymce.models import HTMLField


class HelpCenterTopic(models.Model):
    title = models.CharField(max_length=200)
    content = HTMLField()  # TinyMCE field
    icon = models.ImageField(upload_to="help_icons/")

    def __str__(self):
        return self.title
