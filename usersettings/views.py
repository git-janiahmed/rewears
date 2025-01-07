from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView,
    DetailView,
    DeleteView,
    UpdateView,
    FormView,
)
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from accounts.models import UserProfile
from .forms import DeleteAccountForm, UserProfileForm, ProfileSettingsForm
from .models import Feedback, UserDeletionRequest


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "usersettings/user_profile.html"
    success_url = reverse_lazy("userprofile")

    def get_object(self, queryset=None):
        # Ensure the logged-in user can only edit their own profile
        return UserProfile.objects.get(user=self.request.user)


class ProfileSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileSettingsForm
    template_name = "usersettings/user_settings.html"
    success_url = reverse_lazy("usersettings")

    def get_object(self, queryset=None):
        return UserProfile.objects.get(user=self.request.user)


# from django.views.generic import TemplateView, FormView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib.auth.models import User
# from django.urls import reverse_lazy
# from django.http import HttpResponseRedirect
# from django.contrib import messages
# from .forms import AccountDeletionForm


# class DeleteAccountView(LoginRequiredMixin, FormView):
#     template_name = "usersettings/delete_account.html"
#     form_class = AccountDeletionForm
#     success_url = reverse_lazy("account_deleted")

#     def form_valid(self, form):
#         # Process the feedback
#         feedback = form.cleaned_data["feedback"]
#         confirmation = form.cleaned_data["confirmation"]

#         if confirmation:
#             # Save feedback if needed (log or database)
#             print(f"User feedback: {feedback}")  # Example

#             # Delete the user account
#             user = self.request.user
#             user.delete()

#             # Add a success message (optional)
#             messages.success(
#                 self.request, "Your account has been successfully deleted."
#             )
#             return super().form_valid(form)
#         else:
#             form.add_error(
#                 "confirmation", "You must confirm before deleting your account."
#             )
#             return self.form_invalid(form)


# class AccountDeletedConfrimView(TemplateView):
#     template_name = "usersettings/delete_confrim.html"


# class AccountDeletedView(TemplateView):
#     template_name = "usersettings/account_deleted.html"


from .models import UserDeletionRequest
from django.contrib import messages


class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = "usersettings/delete_confrim.html"
    form_class = DeleteAccountForm
    success_url = reverse_lazy("account_deactivated")  # Updated redirect URL

    def form_valid(self, form):
        feedback = form.cleaned_data.get("feedback")
        confirmation = form.cleaned_data.get("confirmation")

        if confirmation:
            # Save feedback

            if feedback:
                Feedback.objects.create(user=self.request.user, feedback_text=feedback)

            # Mark user account for deletion
            UserDeletionRequest.objects.create(user=self.request.user)

            # Optionally deactivate user login immediately
            self.request.user.is_active = False
            self.request.user.save()

            messages.success(
                self.request,
                "Your account has been deactivated. It will be permanently deleted within 30 days.",
            )
            return super().form_valid(form)
        else:
            form.add_error(
                "confirmation", "You must confirm before deleting your account."
            )
            return self.form_invalid(form)


class AccountDeactivatedView(TemplateView):
    template_name = "usersettings/deleted.html"


from .models import Report
from .forms import ReportForm


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = Report
    form_class = ReportForm
    template_name = "report/report_form.html"
    success_url = reverse_lazy("report_success")

    def get_initial(self):
        initial = super().get_initial()
        initial["reporter_email"] = self.request.user.email
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        reported_user = get_object_or_404(
            UserProfile, id=self.kwargs["reported_user_id"]
        )
        kwargs["reported_user"] = reported_user.user
        return kwargs

    def form_valid(self, form):
        form.instance.reporter = self.request.user
        form.instance.reported_user = form.cleaned_data["reported_user"]
        form.instance.reporter_email = self.request.user.email
        return super().form_valid(form)


class ReportSuccessView(TemplateView):
    template_name = "report/report_success.html"
