from django.urls import path
from .views import (
    AdminDashboardView,
    AdminUserListView,
    AdminUserDetailView,
    AdminUserStatusToggleView,
    AdminOrderListView,
    AdminOrderStatusUpdateView,
)

urlpatterns = [
    # Dashboard
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),

    # Users
    path("users/", AdminUserListView.as_view(), name="admin-users-list"),
    path("users/<int:id>/", AdminUserDetailView.as_view(), name="admin-user-detail"),
    path("users/<int:id>/toggle-active/", AdminUserStatusToggleView.as_view(), name="admin-user-toggle"),

    # Orders
    path("orders/", AdminOrderListView.as_view(), name="admin-orders-list"),
    path("orders/<int:id>/status/", AdminOrderStatusUpdateView.as_view(), name="admin-order-status"),
]
