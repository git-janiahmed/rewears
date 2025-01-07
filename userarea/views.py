from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView,
    DetailView,
    DeleteView,
    UpdateView,
    View,
)
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from .forms import ProductForm, ProductImageForm, ProductUpdateForm
from .models import Product, ProductImage, Category, Brand, Size, Color
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Follow, UserProfile

from django.contrib.auth.models import User


# notifications views

from .models import Notification
from pusher import Pusher
from django.conf import settings

# Initialize Pusher
pusher_client = Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True,
)


class MarkAsReadView(LoginRequiredMixin, View):
    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id, recipient=request.user
            )
            notification.mark_as_read()
            return JsonResponse({"success": True})
        except Notification.DoesNotExist:
            return JsonResponse({"success": False}, status=404)


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "userDashboard/notifications.html"
    context_object_name = "notifications_list"
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by(
            "-created_at"
        )


def send_notification(user, message, notification_type="GENERAL", link=""):

    notification = Notification.objects.create(
        recipient=user, message=message, notification_type=notification_type, link=link
    )
    # Trigger Pusher event
    pusher_client.trigger(
        f"notifications-{user.id}",
        "new-notification",
        {
            "id": notification.id,
            "message": str(notification.message),  # Ensure message is a string
            "type": str(notification.notification_type),  # Ensure type is a string
            "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "link": str(notification.link),  # Ensure link is a string
        },
    )

    print("Notification sent successfully")


class UserProfileView(DetailView):
    model = User
    template_name = "pages/public_profile.html"
    context_object_name = "profile_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.filter(user=self.object, status="active")
        # Handle follow status
        if self.request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=self.request.user.userprofile,
                following=self.object.userprofile,
            ).exists()
            context["is_following"] = is_following
        else:
            context["is_following"] = False
        return context


class UserDashboardIndex(LoginRequiredMixin, ListView):
    model = Product
    template_name = "userDashboard/index.html"
    context_object_name = "products"

    def get_queryset(self):
        queryset = Product.objects.filter(user=self.request.user).prefetch_related(
            "images"
        )
        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status"] = self.request.GET.get("status", "all")
        return context


from django.db import IntegrityError


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "userDashboard/product_upload.html"
    success_url = reverse_lazy("userdashboardIndex")

    def form_valid(self, form):
        # Save the product instance with the current user
        product = form.save(commit=False)
        product.user = self.request.user

        # Get the most specific category ID from the form data
        category_id = (
            self.request.POST.get("sub_sub_category", None)
            or self.request.POST.get("sub_category", None)
            or self.request.POST.get("main_category", None)
        )

        if category_id:
            # Ensure the category exists
            product.category = get_object_or_404(Category, id=category_id)
        else:
            # Handle the case where no category is provided
            form.add_error(None, "Please select a category.")
            return self.form_invalid(form)

        # Handle brand name or selection
        brand_name = form.cleaned_data.get("brand_name")
        if brand_name:
            brand, created = Brand.objects.get_or_create(
                name=brand_name, category=product.category
            )
            product.brand = brand
        else:
            brand_id = form.cleaned_data.get("brand")
            if brand_id:
                product.brand = get_object_or_404(Brand, id=brand_id)
            else:
                form.add_error(None, "Please select or enter a brand.")
                return self.form_invalid(form)

        try:
            product.save()
        except IntegrityError:
            form.add_error(
                None, "An error occurred while saving the product. Please try again."
            )
            return self.form_invalid(form)

        # Handle product images
        images = self.request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(product=product, image=image)

        form.save_m2m()  # Save many-to-many fields if any
        return super().form_valid(form)

    def get_success_url(self):
        return self.success_url


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductUpdateForm
    template_name = "userDashboard/product_update.html"
    success_url = reverse_lazy("userdashboardIndex")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_categories = Category.objects.filter(parent__isnull=True)
        context["main_categories"] = main_categories
        context["product_images"] = (
            self.object.images.all()
        )  # Add images to the context
        return context

    def form_valid(self, form):
        # Save the product instance with the current user
        product = form.save(commit=False)
        product.user = self.request.user

        # Get the most specific category ID from the form data
        category_id = (
            self.request.POST.get("sub_sub_category", None)
            or self.request.POST.get("sub_category", None)
            or self.request.POST.get("main_category", None)
        )
        if category_id:
            product.category = Category.objects.get(id=category_id)

        product.save()

        # Handle product images
        images = self.request.FILES.getlist("images")
        if images:
            # Remove existing images if new ones are uploaded
            ProductImage.objects.filter(product=product).delete()
            for image in images:
                ProductImage.objects.create(product=product, image=image)

        form.save_m2m()  # Save many-to-many fields if any
        return super().form_valid(form)


from django.apps import apps


class ProductDetailView(DetailView):
    model = Product
    template_name = "pages/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.object.user
        context["more_items"] = Product.objects.filter(
            user=seller, status="active"
        ).exclude(id=self.object.id)[:5]

        if self.request.user.is_authenticated:
            context["wishlist"] = self.request.user.wishlist.values_list(
                "product_id", flat=True
            )
            # Dynamically import the Chat model to avoid circular import
            Chat = apps.get_model("chatapp", "Chat")
            # Check if a chat already exists between the buyer and seller for this product
            chat = Chat.objects.filter(
                product=self.object, participants=self.request.user
            ).first()
            context["chat"] = chat
        else:
            context["wishlist"] = []
            context["chat"] = None

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     product = self.get_object()
    #     chat = Chat.objects.filter(participants=user, product=product).first()
    #     context["chat"] = chat
    #     return context


class OrderConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = "pages/order_confirmation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, id=product_id)
        context["product"] = product
        return context


def get_subcategories(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = Category.objects.filter(parent=category)
    subcategories_list = list(subcategories.values("id", "name", "icon_img"))
    return JsonResponse(subcategories_list, safe=False)


def get_brands(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    brands = Brand.objects.filter(category=category)
    brands_list = list(brands.values("id", "name"))
    return JsonResponse(brands_list, safe=False)


def get_sizes(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    sizes = Size.objects.filter(category=category)
    sizes_list = list(sizes.values("id", "name"))
    return JsonResponse(sizes_list, safe=False)


def get_brands_and_sizes(request, category_id):
    subcategory = get_object_or_404(Category, id=category_id)
    brands = Brand.objects.filter(category=subcategory)
    sizes = Size.objects.filter(category=subcategory)

    brands_list = list(brands.values("id", "name"))
    sizes_list = list(sizes.values("id", "name"))

    data = {
        "brands": brands_list,
        "sizes": sizes_list,
    }
    return JsonResponse(data)


from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from .models import Product, Wishlist


class AddToWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )
        if created:
            return JsonResponse({"status": "added"})
        else:
            return JsonResponse({"status": "exists"})


class RemoveFromWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
        if wishlist_item.exists():
            wishlist_item.delete()
            return JsonResponse({"status": "removed"})
        else:
            return JsonResponse({"status": "not_found"})


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = "pages_front/wishlist.html"
    context_object_name = "wishlist_items"
    paginate_by = 20

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("product")


class ToggleWishlistView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user, product=product
        )
        if created:
            return JsonResponse({"status": "added"})
        else:
            wishlist_item.delete()
            return JsonResponse({"status": "removed"})


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "userDashboard/product_confirm_delete.html"  # Replace with your confirmation template
    success_url = reverse_lazy(
        "userdashboardIndex"
    )  # Redirect to your desired page after deletion

    def test_func(self):
        # Ensure the logged-in user is the owner of the product
        product = self.get_object()
        return self.request.user == product.user


# Follow views

from django.http import JsonResponse
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction


class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                # Get the profile of the user being viewed/followed
                target_profile = get_object_or_404(
                    UserProfile, user__id=self.kwargs.get("pk")
                )

                # Check if user is trying to follow themselves
                if request.user.userprofile == target_profile:
                    return JsonResponse(
                        {"error": "You cannot follow yourself."}, status=400
                    )

                # Check if already following
                follow_obj = Follow.objects.filter(
                    follower=request.user.userprofile, following=target_profile
                ).first()

                if follow_obj:
                    # Unfollow
                    follow_obj.delete()
                    status = "unfollowed"
                else:
                    # Follow
                    Follow.objects.create(
                        follower=request.user.userprofile, following=target_profile
                    )
                    status = "followed"
                    link = reverse_lazy(
                        "UserProfileView", kwargs={"pk": request.user.id}
                    )
                    message = f"{request.user.username} followed you"
                    send_notification(
                        target_profile.user,
                        message,
                        notification_type="FOLLOW",
                        link=link,
                    )

                # Get the updated counts for the target profile only
                target_profile.refresh_from_db()  # Refresh to get updated counts

                return JsonResponse(
                    {
                        "status": status,
                        "followers_count": target_profile.followers_count,
                        "following_count": target_profile.following_count,
                    }
                )

        except Exception as e:
            return JsonResponse(
                {"error": "An error occurred while processing your request."},
                status=500,
            )


class FollowersListView(ListView):
    model = Follow
    template_name = "userDashboard/follow/followers_list.html"
    context_object_name = "followers"

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, pk=self.kwargs.get("pk"))
        return Follow.objects.filter(following=user_profile)


class FollowingListView(ListView):
    model = Follow
    template_name = "userDashboard/follow/following_list.html"
    context_object_name = "following"

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, pk=self.kwargs.get("pk"))
        return Follow.objects.filter(follower=user_profile)
