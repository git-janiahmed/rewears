from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy

from .models import AwaitingUser
from .forms import CommingSoonForm

# Create your views here.


class CommingSoonRegister(CreateView):
    template_name = "commingsoon/index.html"
    form_class = CommingSoonForm
    success_url = reverse_lazy("commingSucess")


class CommingSoonSucess(TemplateView):
    template_name = "commingsoon/thankyou.html"
