from django.urls import path
from . import views
from .import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns=[
    path('register/',views.RegisterView.as_view()),
    path('login/',views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

  
    

]