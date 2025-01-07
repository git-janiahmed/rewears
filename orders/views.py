from django.views.generic import ListView, CreateView, View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from .models import Order, Review
from userarea.models import Product
from userarea.views import send_notification


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    template_name = "order/order_confirm.html"
    fields = []  # No additional fields needed, set fields in the view logic

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_id"])
        context = {"product": product}
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, pk=self.kwargs["product_id"])
        seller = product.user
        buyer = request.user

        # Check if the buyer is not the same as the seller
        if buyer == seller:
            return redirect("product_detail", product_id=product.id)

        # Create the order
        Order.objects.create(
            product=product, buyer=buyer, seller=seller, status="pending"
        )

        message = f"Your received a new order from {buyer}"
        link = reverse_lazy("manage_orders")
        send_notification(
            seller, message, notification_type="Order confirmed", link=link
        )
        return redirect("order_list")


from chatapp.models import Chat


class BuyerOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order/buyer_order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        # Filter orders where the current user is the buyer
        return Order.objects.filter(buyer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            orders = context["orders"]
            for order in orders:
                chat = Chat.objects.filter(
                    product=order.product, participants=self.request.user
                ).first()
                order.chat = chat
        return context


class SellerOrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order/seller_order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        # Filter orders where the current user is the seller
        return Order.objects.filter(seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            orders = context["orders"]
            for order in orders:
                chat = Chat.objects.filter(
                    product=order.product, participants=self.request.user
                ).first()
                order.chat = chat
        return context


class ConfirmOrderView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, seller=request.user)
        order.status = "confirmed"
        order.save()
        product = get_object_or_404(Product, pk=order.product.id, user=request.user)
        product.status = "reserved"
        product.save()
        message = f"{request.user.username} {order.status} your order"
        link = reverse_lazy("order_list")
        send_notification(
            order.buyer, message, notification_type="Order confirmed", link=link
        )
        return redirect("manage_orders")


class DeliverOrderView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        order = get_object_or_404(Order, pk=pk, seller=request.user)
        order.status = "delivered"
        order.save()
        product = get_object_or_404(Product, pk=order.product.id, user=request.user)
        product.status = "sold"
        product.save()
        message = f"{request.user.username} marked your Order {order.status}, don't forget to review the product/seller."
        link = reverse_lazy("order_list")

        send_notification(
            order.buyer, message, notification_type="Order Completed", link=link
        )

        return redirect("manage_orders")


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    template_name = "order/review_create.html"
    fields = ["rating", "comment"]

    def form_valid(self, form):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        form.instance.buyer = user_profile
        form.instance.order = get_object_or_404(
            Order,
            pk=self.kwargs["order_id"],
            buyer=self.request.user,
            status="delivered",
        )
        form.instance.seller = get_object_or_404(
            UserProfile, user=form.instance.order.seller
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = get_object_or_404(Order, pk=self.kwargs["order_id"])
        product = order.product  # Assuming Order has a ForeignKey to Product
        context["product"] = product
        return context

    def get_success_url(self):
        message = f"{self.request.user.username} left a review for your product. Don't forget to check it out."
        order = get_object_or_404(Order, pk=self.kwargs["order_id"])
        link = reverse_lazy("reviews_list")

        send_notification(order.seller, message, notification_type="Review", link=link)
        return reverse_lazy("order_list")


from django.db.models import Avg, Count
from accounts.models import UserProfile


class ReviewsList(ListView):
    model = Review
    template_name = "order/reviews_list.html"
    context_object_name = "reviews"

    def get_queryset(self):
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        return Review.objects.filter(seller=user_profile).select_related("buyer")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = get_object_or_404(UserProfile, user=self.request.user)
        reviews = Review.objects.filter(seller=user_profile)
        context["reviews_count"] = reviews.count()
        context["average_rating"] = reviews.aggregate(Avg("rating"))["rating__avg"]
        context["profile_user"] = user_profile
        return context
