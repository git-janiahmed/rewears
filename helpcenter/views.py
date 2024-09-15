from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from .models import HelpCenterTopic

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
