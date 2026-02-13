from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from orders.models import Order

from .serializers import (
    AdminDashboardSerializer,
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminOrderListSerializer,
    AdminOrderStatusUpdateSerializer,
)

User = get_user_model()


# -------------------------
# Admin Dashboard
# -------------------------
class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()

        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status="pending").count()
        paid_orders = Order.objects.filter(status="paid").count()
        shipped_orders = Order.objects.filter(status="shipped").count()
        delivered_orders = Order.objects.filter(status="delivered").count()
        cancelled_orders = Order.objects.filter(status="cancelled").count()

        data = {
            "total_users": total_users,
            "active_users": active_users,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "paid_orders": paid_orders,
            "shipped_orders": shipped_orders,
            "delivered_orders": delivered_orders,
            "cancelled_orders": cancelled_orders,
        }

        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Admin Users: list
# -------------------------
class AdminUserListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by("-date_joined")
        serializer = AdminUserListSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Admin Users: detail
# -------------------------
class AdminUserDetailView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminUserDetailSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Admin Users: toggle active status
# -------------------------
class AdminUserStatusToggleView(APIView):
    """
    Toggle is_active True/False
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        # Prevent admin disabling themselves (optional but recommended)
        if user.id == request.user.id:
            return Response(
                {"error": "You cannot disable your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_active = not user.is_active
        user.save()

        return Response(
            {
                "message": "User status updated.",
                "id": user.id,
                "is_active": user.is_active,
            },
            status=status.HTTP_200_OK
        )


# -------------------------
# Admin Orders: list all
# -------------------------
class AdminOrderListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        orders = Order.objects.select_related("user").prefetch_related("items").order_by("-created_at")
        serializer = AdminOrderListSerializer(orders, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# -------------------------
# Admin Orders: update status
# -------------------------
class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdminOrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        # Safety rules (simple real-life rules)
        if order.status in ["delivered", "cancelled"]:
            return Response(
                {"error": f"Cannot change status of a {order.status} order."},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        # return updated order with details
        return Response(
            AdminOrderListSerializer(order, context={"request": request}).data,
            status=status.HTTP_200_OK
        )
