from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import smart_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import Profile
from accounts.tasks import send_reset_password_email_task, send_verification_email_task

from .serializers import (
    ChangePasswordSerializer,
    CreateJwtTokenSerializer,
    LoginSerializer,
    PasswordResetEmailSerializer,
    PasswordResetTokenValidateSerializer,
    ProfileSerializer,
    RegisterUserSerializer,
    ResendActivationLinkSerializer,
)
from ...services import create_user

from ...utils import activate_user

User = get_user_model()


class RegisterUserView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        validated_data = serializer.validated_data
        try:
            create_user(
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                password=validated_data["password"],
            )

        except Exception as e:
            return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        email = validated_data["email"]
        data = {
            # post method will return all fields but password shouldn't be returned
            "email": email,
            "first_name": validated_data["first_name"],
            "last_name": validated_data["last_name"],
        }
        user = get_object_or_404(User, email=email)

        user_id = user.id
        receiver = email
        current_site = get_current_site(request).domain
        mail_subject = "Please verify your email"
        email_template = "accounts/email/email_verification.html"
        send_verification_email_task.delay(
            user_id, receiver, current_site, mail_subject, email_template
        )
        return Response(data, status=status.HTTP_201_CREATED)


class UserActivationView(APIView):
    def get(self, request, token, *args, **kwargs):
        return activate_user(token)


class TokenLoginView(ObtainAuthToken):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class TokenLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateJwtTokenView(TokenObtainPairView):
    """
    View for creating a JWT token for user to authenticate
    """

    serializer_class = CreateJwtTokenSerializer


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        user = self.request.user
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        if not user.check_password(validated_data["old_password"]):
            # check_password is a built-in function in Django's User model that takes a password as an argument,
            # and returns True if the password matches the one stored in the database for the user, or False otherwise.
            return Response(
                {"detail": "Wrong password."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # set_password also hashes the password that the user will get
        user.set_password(validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class ResendActivationLinkView(generics.GenericAPIView):
    serializer_class = ResendActivationLinkSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        user_id = user.id
        receiver = user.email
        current_site = get_current_site(request).domain
        mail_subject = "Please verify your email"
        email_template = "accounts/email/email_verification.html"
        send_verification_email_task.delay(
            user_id, receiver, current_site, mail_subject, email_template
        )
        return Response(
            {"detail": "Activation link resent successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordResetEmailView(generics.GenericAPIView):
    serializer_class = PasswordResetEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        user_id = user.id
        receiver = user.email
        current_site = get_current_site(request).domain
        mail_subject = "Password Reset"
        email_template = "accounts/email/reset_password_email.html"
        send_reset_password_email_task.delay(
            user_id, receiver, current_site, mail_subject, email_template
        )

        return Response(
            {"success": "We have sent you a link to reset your password"},
            status=status.HTTP_200_OK,
        )


class PasswordResetTokenValidateView(generics.GenericAPIView):
    serializer_class = PasswordResetTokenValidateSerializer

    def put(self, request, uidb64, token):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        password = serializer.validated_data["password"]
        uidb64 = self.kwargs["uidb64"]
        token = self.kwargs["token"]

        id = smart_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response(
                {"detail": "The reset link is invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(password)
        user.save()
        return Response(
            {"detail": "You have successfully reset your password."},
            status=status.HTTP_200_OK,
        )

    def get(self, request, uidb64, token):

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {"detail": "The reset link is invalid"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"detail": "Token is not valid, please request a new one"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_200_OK)
