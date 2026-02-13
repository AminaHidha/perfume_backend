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
    path('profile/', views.ProfileView.as_view()),   # ✅ NEW
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("forgot-password/", views.ForgotPasswordView.as_view()),
    path("reset-password/", views.ResetPasswordView.as_view()),
    path("google-login/", views.GoogleLoginView.as_view()),

]