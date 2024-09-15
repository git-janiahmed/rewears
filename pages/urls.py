from django.urls import path, include
from .views import (
    WishListView,
    AboutView,
    AdvertisingView,
    HowitWorks,
    CategoryProductsView,
    ProductSearchView,
    PublicProfileView,
    PublicReviewListView,
    HomeIndexView,
)

urlpatterns = [
    path("", HomeIndexView.as_view(), name="homepage"),
    path("wishlist", WishListView.as_view(), name="wishlist"),
    path("about", AboutView.as_view(), name="about"),
    path("advertising", AdvertisingView.as_view(), name="advertising"),
    path("howitworks", HowitWorks.as_view(), name="howitworks"),
    path(
        "category/<int:category_id>/",
        CategoryProductsView.as_view(),
        name="category_products",
    ),
    path("search/", ProductSearchView.as_view(), name="search_products"),
    path("profile/<str:username>/", PublicProfileView.as_view(), name="public_profile"),
    path(
        "user/<str:username>/reviews/",
        PublicReviewListView.as_view(),
        name="public_reviews",
    ),
]
