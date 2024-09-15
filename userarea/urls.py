from django.urls import path
from .views import (
    UserDashboardIndex,
    ProductCreateView,
    ProductDetailView,
    get_subcategories,
    get_brands,
    get_brands_and_sizes,
    ProductUpdateView,
    ProductDeleteView,
)
from .views import AddToWishlistView, RemoveFromWishlistView, WishlistView

urlpatterns = [
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path(
        "wishlist/add/<int:product_id>/",
        AddToWishlistView.as_view(),
        name="add_to_wishlist",
    ),
    path(
        "wishlist/remove/<int:product_id>/",
        RemoveFromWishlistView.as_view(),
        name="remove_from_wishlist",
    ),
    path("", UserDashboardIndex.as_view(), name="userdashboardIndex"),
    path("upload/", ProductCreateView.as_view(), name="product_upload"),
    path(
        "product/update/<int:pk>/", ProductUpdateView.as_view(), name="product_update"
    ),
    path(
        "get_subcategories/<int:category_id>/",
        get_subcategories,
        name="get_subcategories",
    ),
    path("get_brands/<int:category_id>/", get_brands, name="get_brands"),
    path(
        "get_brands_and_sizes/<int:category_id>/",
        get_brands_and_sizes,
        name="get_brands_and_sizes",
    ),
    path(
        "product/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"
    ),
    path("product/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]
