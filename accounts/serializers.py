from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


# -----------------------------
# Register
# -----------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


# -----------------------------
# Login
# -----------------------------
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        # IMPORTANT:
        # Your USERNAME_FIELD is 'email', so authenticate expects "username"
        user = authenticate(
            username=data["email"],  # ✅ correct
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid Email Or Password")

        if user.status != "Active":
            raise serializers.ValidationError("User Account Is Inactive")

        data["user"] = user
        return data


# -----------------------------
# User data for profile/admin
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "status",
            "phone",
            "is_active",
            "date_joined",
        ]


# -----------------------------
# Forgot Password (send email)
# -----------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self):
        email = self.validated_data["email"]

        # Security: don't reveal if email exists
        user = User.objects.filter(email=email).first()
        if not user:
            return

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        reset_link = f"{frontend_url}/reset-password/{uidb64}/{token}"

        subject = "Reset your password"
        message = (
            f"Hi {user.username},\n\n"
            f"Click the link below to reset your password:\n\n"
            f"{reset_link}\n\n"
            f"If you did not request this, ignore this email."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER),
            recipient_list=[email],
            fail_silently=False,
        )


# -----------------------------
# Reset Password (set new pass)
# -----------------------------
class ResetPasswordSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            user = User.objects.get(pk=uid)
        except Exception:
            raise serializers.ValidationError("Invalid reset link")

        if not token_generator.check_token(user, data["token"]):
            raise serializers.ValidationError("Invalid or expired token")

        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        new_password = self.validated_data["new_password"]

        user.set_password(new_password)
        user.save()
        return user
    
# -----------------------------------
# google auth(continuw with google)
# -----------------------------------


class GoogleLoginSerializer(serializers.Serializer):
    credential = serializers.CharField()  # Google ID token

    def validate(self, data):
        credential = data["credential"]
        request = google_requests.Request()

        try:
            # ✅ Verify token with Google
            payload = id_token.verify_oauth2_token(
                credential,
                request,
                audience=None  # we will check in view using settings
            )
        except Exception:
            raise serializers.ValidationError("Invalid Google token")

        data["payload"] = payload
        return data