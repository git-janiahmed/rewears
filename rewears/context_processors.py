# core/context_processors.py

from userarea.models import Category, Notification
from chatapp.models import Chat


def category_context(request):
    main_categories = Category.objects.filter(parent__isnull=True)
    notifications = 0
    unread_notifications_count = 0
    unread_messages_count = 0
    if request.user.is_authenticated:  # Ensure the user is logged in
        notifications = Notification.objects.filter(recipient=request.user).order_by(
            "-created_at"
        )[
            :10
        ]  # Fetch the latest 10 notifications

        unread_notifications_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        )[:10].count()

        unread_messages_count = Chat.total_unread_messages_count(request.user)

    return {
        "main_categories": main_categories,
        "notifications": notifications,
        "unread_messages_count": unread_messages_count,
        "unread_notifications_count": unread_notifications_count,
    }
