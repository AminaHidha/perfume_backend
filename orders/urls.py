from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),          # GET all orders
    path('create/', views.OrderCreateView.as_view(), name='order-create'),# POST create order
    path('<int:id>/', views.OrderDetailView.as_view(), name='order-detail'), # GET single order
]
