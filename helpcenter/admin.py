from django.contrib import admin
from .models import (
    HelpCenterTopic,
    PrivacyPolicy,
    TermsAndConditions,
    ContactMessage,
    Update,
)
from .views import send_update_notification


class UpdateAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Only send notification on creation
            send_update_notification(obj)


admin.site.register(HelpCenterTopic)
admin.site.register(PrivacyPolicy)
admin.site.register(TermsAndConditions)
admin.site.register(ContactMessage)
admin.site.register(Update, UpdateAdmin)
