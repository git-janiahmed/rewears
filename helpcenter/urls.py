from django.urls import path, include
from .views import (
    HelpHome,
    HelpTopicDetailView,
    PrivacyPolicyView,
    TermsAndConditionsView,
    ContactView,
    UpdateListView,
    UpdateDetailView,
)

urlpatterns = [
    path("helpcenter/", HelpHome.as_view(), name="helpcenter"),
    path(
        "helpcenter/<int:pk>/", HelpTopicDetailView.as_view(), name="help_topic_detail"
    ),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path(
        "terms-and-conditions/",
        TermsAndConditionsView.as_view(),
        name="terms_and_conditions",
    ),
    path("contact/", ContactView.as_view(), name="contact"),
    path("updates/", UpdateListView.as_view(), name="updates"),
    path("updates/<int:pk>/", UpdateDetailView.as_view(), name="update_detail"),
]
