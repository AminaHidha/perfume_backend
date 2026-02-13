from rest_framework import serializers
from django.contrib.auth import get_user_model

from orders.models import Order
from orders.serializers import OrderReadSerializer  # reuse your existing order read serializer

User = get_user_model()


# -------------------------
# Admin: Users
# -------------------------
class AdminUserListSerializer(serializers.ModelSerializer):
    """
    Admin list view: lightweight info.
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "date_joined",
        ]


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """
    Admin detail view: more info + order count.
    """
    orders_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "date_joined",
            "orders_count",
        ]

    def get_orders_count(self, obj):
        # related_name='orders' in your Order model
        return obj.orders.count()


# -------------------------
# Admin: Dashboard
# -------------------------
class AdminDashboardSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    paid_orders = serializers.IntegerField()
    shipped_orders = serializers.IntegerField()
    delivered_orders = serializers.IntegerField()
    cancelled_orders = serializers.IntegerField()


# -------------------------
# Admin: Orders list
# (Reusing your OrderReadSerializer is good)
# -------------------------
class AdminOrderListSerializer(OrderReadSerializer):
    """
    Same as OrderReadSerializer but for admin (shows all users' orders).
    """
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(OrderReadSerializer.Meta):
        fields = OrderReadSerializer.Meta.fields + [
            "user_id",
            "user_username",
            "user_email",
        ]


# -------------------------
# Admin: Update order status
# -------------------------
class AdminOrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=["pending", "paid", "shipped", "delivered", "cancelled"]
    )
