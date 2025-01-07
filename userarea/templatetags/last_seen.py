from django import template
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Avg

register = template.Library()


@register.filter
def time_since_last_seen(last_seen):
    if not last_seen:
        return "Never"

    delta = now() - last_seen
    if delta < timedelta(minutes=1):
        return "Just now"
    elif delta < timedelta(hours=1):
        return f"{int(delta.seconds / 60)} minutes ago"
    elif delta < timedelta(days=1):
        return f"{int(delta.seconds / 3600)} hours ago"
    else:
        return f"{delta.days} days ago"


@register.filter
def to(value, arg):
    return range(value, arg + 1)


@register.filter
def average_rating(user_profile):
    reviews = user_profile.seller_reviews.all()
    avg_rating = reviews.aggregate(Avg("rating"))["rating__avg"]
    return avg_rating or 0


@register.filter
def reviews_count(user_profile):
    return user_profile.seller_reviews.count()


@register.filter
def average_rating_percentage(user_profile):
    avg_rating = average_rating(user_profile)
    return (avg_rating / 5) * 100
