from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    ListView,
    CreateView,
    TemplateView,
    DetailView,
    DeleteView,
    UpdateView,
)
from django.views.generic.base import TemplateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.http import JsonResponse
from .forms import ProductForm, ProductImageForm, ProductUpdateForm
from .models import Product, ProductImage, Category, Brand, Size, Color
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from chatapp.models import Chat


class UserDashboardIndex(LoginRequiredMixin, ListView):
    model = Product
    template_name = "userDashboard/index.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user).prefetch_related("images")


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "userDashboard/product_upload.html"
    success_url = reverse_lazy("userdashboardIndex")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        main_categories = Category.objects.filter(parent__isnull=True)
        context["main_categories"] = main_categories
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


class ProductDetailView(DetailView):
    model = Product
    template_name = "pages/product_detail.html"
    context_object_name = "product"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     user = self.request.user
    #     product = self.get_object()
    #     chat = Chat.objects.filter(participants=user, product=product).first()
    #     context["chat"] = chat
    #     return context


def get_subcategories(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    subcategories = Category.objects.filter(parent=category)
    subcategories_list = list(subcategories.values("id", "name"))
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


class AddToWishlistView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return redirect("wishlist")  # Redirect to the wishlist page


class RemoveFromWishlistView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        wishlist_item = Wishlist.objects.filter(user=request.user, product=product)
        if wishlist_item.exists():
            wishlist_item.delete()
        return redirect("wishlist")  # Redirect to the wishlist page


class WishlistView(ListView):
    model = Wishlist
    template_name = "pages_front/wishlist.html"
    context_object_name = "wishlist_items"

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("product")


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
