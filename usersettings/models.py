from django.db import models

# Create your models here.


from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class UserDeletionRequest(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def delete_account(self):
        """Method to delete the associated user account."""
        self.user.delete()
        self.is_deleted = True
        self.save()


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_text = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Feedback from {self.user.username if self.user else 'Anonymous'} on {self.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}"


class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports")
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reported_by",
        null=True,
        blank=True,
    )
    subject = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    media_file = models.FileField(upload_to="reports/", null=True, blank=True)
    reporter_email = models.EmailField()

    def __str__(self):
        return f"Report by {self.reporter.username} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
