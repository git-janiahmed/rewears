from django.views.generic import TemplateView, ListView, DetailView
from django.urls import reverse_lazy
from userarea.models import Category, Product, Brand, Color, Size
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from orders.models import Review
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


class HomeIndexView(TemplateView):
    template_name = "pages_front/index.html"


class WishListView(LoginRequiredMixin, TemplateView):
    login_url = "/login/"
    template_name = "pages_front/wishlist.html"


class AboutView(TemplateView):
    template_name = "pages_front/about.html"


class AdvertisingView(TemplateView):
    template_name = "pages_front/advertising.html"


class HowitWorks(TemplateView):
    template_name = "pages_front/howitworks.html"


from django.db.models import Q


class CategoryProductsView(ListView):
    model = Product
    template_name = "pages_front/category_products.html"
    context_object_name = "products"
    paginate_by = 12  # Number of products per page

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        category = Category.objects.get(id=category_id)

        # Get all child categories of the selected category
        child_categories = Category.objects.filter(
            Q(id=category_id) | Q(parent=category_id) | Q(parent__parent=category_id)
        )

        # Filter products by the category and its subcategories
        queryset = Product.objects.filter(
            category__in=child_categories, status="active"
        )

        # Apply filters if they are in the request
        brand = self.request.GET.get("brand")
        size = self.request.GET.get("size")
        color = self.request.GET.get("color")

        if brand:
            queryset = queryset.filter(brand__id=brand)
        if size:
            queryset = queryset.filter(size__id=size)
        if color:
            queryset = queryset.filter(colors__id=color)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs["category_id"]
        category = Category.objects.get(id=category_id)

        # Get all child categories of the selected category
        child_categories = Category.objects.filter(
            Q(id=category_id) | Q(parent=category_id)
        )

        context["category"] = category
        context["brands"] = Brand.objects.filter(category__in=child_categories)
        context["sizes"] = Size.objects.filter(category__in=child_categories)
        context["colors"] = (
            Color.objects.all()
        )  # Assuming colors are not category-specific
        return context


from django.shortcuts import render
from django.db.models import Q


class ProductSearchView(ListView):
    model = Product
    template_name = "pages/search_results.html"
    context_object_name = "products"

    def get_queryset(self):
        query = self.request.GET.get("q")  # Get the search term from the input field
        if query:
            return Product.objects.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)  # Search in title or description
            )
        else:
            return Product.objects.none()  # Return an empty queryset if no query

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q")
        return context


class PublicProfileView(DetailView):
    model = User
    template_name = (
        "pages/public_profile.html"  # Use a dedicated template for public profile
    )
    context_object_name = "profile_user"

    def get_object(self):
        # Fetch user based on username or ID passed in the URL
        return get_object_or_404(User, username=self.kwargs["username"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the products and reviews for the user
        context["products"] = Product.objects.filter(
            user=self.object
        )  # Adjust according to your models
        context["reviews"] = Review.objects.filter(
            seller=self.object
        )  # Adjust according to your models
        return context


class PublicReviewListView(ListView):
    model = Review
    template_name = "pages/public_reviews.html"  # Your template file
    context_object_name = "reviews"
    paginate_by = 10  # Number of reviews per page

    def get_queryset(self):
        # Get the user by username passed in the URL
        self.user_profile = get_object_or_404(User, username=self.kwargs["username"])
        # Filter reviews for the specific user
        return Review.objects.filter(seller=self.user_profile)

    def get_context_data(self, **kwargs):
        # Add additional context to be used in the template
        context = super().get_context_data(**kwargs)
        context["user_profile"] = self.user_profile
        return context
