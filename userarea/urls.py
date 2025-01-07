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
    UserProfileView,
    FollowersListView,
    FollowToggleView,
    FollowingListView,
    ToggleWishlistView,
    OrderConfirmationView,
)
from .views import AddToWishlistView, RemoveFromWishlistView, WishlistView
from .views import NotificationListView, MarkAsReadView, NotificationListView

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
    path(
        "wishlist/toggle/<int:product_id>/",
        ToggleWishlistView.as_view(),
        name="toggle_wishlist",
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
    path("public/profile/<int:pk>/", UserProfileView.as_view(), name="UserProfileView"),
    path("<int:pk>/follow/", FollowToggleView.as_view(), name="follow-toggle"),
    path("<int:pk>/followers/", FollowersListView.as_view(), name="followers"),
    path("<int:pk>/following/", FollowingListView.as_view(), name="following"),
    path("notifications/", NotificationListView.as_view(), name="notification_list"),
    path(
        "notifications/mark-as-read/<int:notification_id>/",
        MarkAsReadView.as_view(),
        name="mark_as_read",
    ),
    path(
        "order/confirmation/<int:pk>/",
        OrderConfirmationView.as_view(),
        name="order_confirmation",
    ),  # Add this line
]
