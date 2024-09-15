from django.urls import path
from .views import (
    OrderCreateView,
    BuyerOrderListView,
    SellerOrderListView,
    ConfirmOrderView,
    DeliverOrderView,
    ReviewCreateView,
    ReviewsList,
)

urlpatterns = [
    # Order Management URLs
    path(
        "order/create/<int:product_id>/", OrderCreateView.as_view(), name="order_create"
    ),
    path("orders/buyer/", BuyerOrderListView.as_view(), name="order_list"),
    path("orders/seller/", SellerOrderListView.as_view(), name="manage_orders"),
    path("orders/confirm/<int:pk>/", ConfirmOrderView.as_view(), name="order_confirm"),
    path("orders/deliver/<int:pk>/", DeliverOrderView.as_view(), name="order_deliver"),
    path(
        "orders/review/<int:order_id>/",
        ReviewCreateView.as_view(),
        name="review_create",
    ),
    path(
        "user/reviews/",
        ReviewsList.as_view(),
        name="reviews_list",
    ),
]
