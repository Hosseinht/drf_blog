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
from blog.api.v1.serializers import FavoritePostSerializer

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
from ...services import create_user, update_profile

from ...utils import activate_user

User = get_user_model()


class RegisterUserView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        try:
            post_user = create_user(
                email=validated_data["email"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                password=validated_data["password"],
            )

        except Exception as e:
            return Response({"detail": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

        email = validated_data["email"]
        user = get_object_or_404(User, email=email)

        user_id = user.id
        receiver = email
        current_site = get_current_site(request).domain
        mail_subject = "Please verify your email"
        email_template = "accounts/email/email_verification.html"
        send_verification_email_task.delay(
            user_id, receiver, current_site, mail_subject, email_template
        )
        serializer = RegisterUserSerializer(post_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

    View for creating a JWT token for user to authenticate with their email.


     - **The view takes in the user's email and password, and creates a JWT token with access and refresh token and also
     email as a payload.**

     - **The token can then be used to authenticate the user in future requests.**

     - **If the user is not verified, the token will not be created and an error will be returned.**


     **Parameters:**

          serializer_class: The serializer class used to validate the user's email and password.

     **Returns:**

         A JWT token that can be used to authenticate the user in future requests.

    """

    serializer_class = CreateJwtTokenSerializer


class ChangePasswordView(generics.GenericAPIView):
    """
    View for changing a user's password.

    This view requires the user to be authenticated. The view takes in the user's old password and new password,
     and changes the user's password to the new password.

     **Parameters:**

       - permission_classes: The permission classes required to access this view. In this case, the user must be
              authenticated.
       - serializer_class: The serializer class used to validate the user's  new passwords.

     **Returns:**

       - A success response with status code 200 if the password was changed successfully.
       - An error response with status code 400 if the old password was incorrect or if the serializer validation
              failed.

    """

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

        user.set_password(validated_data["new_password"])
        # set_password also hashes the password that the user will get
        user.save()

        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating a user's profile.

    - **This view requires the user to be authenticated. The view retrieves the user's profile by getting the `Profile`
     object related to the authenticated user, and then returns the profile data in the response.**

    - **The view  allows updating the user's profile. The view takes in the new profile data in the request,
     validates it using the `ProfileSerializer`, and updates the profile object with the new data. it also allows
     updating user's first and last name.**


    **Parameters:**

       - serializer_class: The serializer class used to serialize and validate the profile data.
       - queryset: The queryset used to retrieve the `Profile` object related to the authenticated user.
       - permission_classes: The permission classes required to access this view. In this case, the user must be
         authenticated.

    **Returns:**

       - A success response with status code 200 if the profile data was retrieved or updated successfully.
       - An error response with status code 400 if the serializer validation failed or if there was an error while
         updating the profile.
    """

    serializer_class = ProfileSerializer
    queryset = (
        Profile.objects.select_related("user")
        .prefetch_related("favoritepost__post__category", "favoritepost__post__author")
        .all()
    )
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj

    def retrieve(self, request, *args, **kwargs):
        profile = self.get_object()
        favorite_post = profile.favoritepost.all()
        serializer = ProfileSerializer(profile, context={"request": request})
        data = serializer.data
        data["favoritepost"] = FavoritePostSerializer(favorite_post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        user = validated_data.pop("user")

        try:
            profile = update_profile(
                instance=instance,
                user=user,
                bio=validated_data["bio"],
                image=validated_data["image"],
                birth_date=validated_data["birth_date"],
            )
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResendActivationLinkView(generics.GenericAPIView):
    """
    View for resending activation link to a user.

    **This view allows the user to request a new activation link in case the activation link has expired or the user did
    not receive it.**

    """

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
    """
    View for password reset

    **This view allows the user to send a request for reseting the password.**

    """

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
    """
    View for validating password reset token

    **This view check the password reset token and validate it.**

    """

    serializer_class = PasswordResetTokenValidateSerializer

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
