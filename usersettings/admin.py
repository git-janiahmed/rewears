from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "submitted_at", "feedback_text")
    search_fields = ("user__username", "feedback_text")
    list_filter = ("submitted_at",)
    date_hierarchy = "submitted_at"
    ordering = ("-submitted_at",)


from django.contrib import admin
from .models import UserDeletionRequest


@admin.register(UserDeletionRequest)
class UserDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "requested_at", "is_deleted")
    list_filter = ("is_deleted",)
    actions = ["permanently_delete_users"]

    @admin.action(description="Permanently delete selected users")
    def permanently_delete_users(self, request, queryset):
        for obj in queryset.filter(is_deleted=False):
            obj.delete_account()
        self.message_user(request, "Selected users have been permanently deleted.")


from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("reporter", "created_at")
    list_filter = ("subject", "created_at")
    search_fields = ("reporter__username", "description")
    readonly_fields = ("created_at",)
