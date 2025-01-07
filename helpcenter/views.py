from django.views.generic import ListView, FormView, DetailView, TemplateView
from django.urls import reverse_lazy
from .models import HelpCenterTopic, Update, PrivacyPolicy, TermsAndConditions
from .forms import ContactForm
from django.contrib import messages
from django.contrib.auth.models import User

from userarea.views import send_notification

# Create your views here.


class HelpHome(ListView):
    model = HelpCenterTopic
    template_name = "helpcenter/topic_list.html"  # Replace with your template path
    context_object_name = "topics"


class HelpTopicDetailView(DetailView):
    model = HelpCenterTopic
    template_name = "helpcenter/topic_detail.html"  # Your detail view template
    context_object_name = "topic"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = (
            HelpCenterTopic.objects.all()
        )  # Pass all topics for the sidebar
        return context


class PrivacyPolicyView(TemplateView):
    template_name = "helpcenter/privacy_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["privacy_policy"] = PrivacyPolicy.objects.first()
        return context


class TermsAndConditionsView(TemplateView):
    template_name = "helpcenter/terms_and_conditions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["terms_and_conditions"] = TermsAndConditions.objects.first()
        return context


class ContactView(FormView):
    template_name = "helpcenter/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Your message has been sent successfully.")
        return super().form_valid(form)


class UpdateListView(ListView):
    model = Update
    template_name = "helpcenter/updates.html"
    context_object_name = "updates"
    ordering = ["-created_at"]


class UpdateDetailView(DetailView):
    model = Update
    template_name = "helpcenter/update_detail.html"
    context_object_name = "update"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["updates"] = Update.objects.all()  # Pass all updates for the sidebar
        return context


def send_update_notification(update):
    users = User.objects.all()
    for user in users:
        link = reverse_lazy("update_detail", kwargs={"pk": update.id})
        send_notification(user, f"New update: {update.title}", "UPDATE", link)
