from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError({"detail": "Passwords do not match."})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        return User.objects.create_user(**validated_data)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password", "confirm_password"]
