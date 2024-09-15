from django.urls import path, include
from .views import HelpHome, HelpTopicDetailView

urlpatterns = [
    path("helpcenter/", HelpHome.as_view(), name="helpcenter"),
    path(
        "helpcenter/<int:pk>/", HelpTopicDetailView.as_view(), name="help_topic_detail"
    ),
]
