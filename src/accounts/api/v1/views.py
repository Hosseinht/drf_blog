from rest_framework import generics, status
from rest_framework.response import Response

from .serializers import RegisterUserSerializer


class RegisterUserAPIView(generics.GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = {
                # post method will return all fields but password shouldn't be returned
                "email": serializer.validated_data["email"],
                "first_name": serializer.validated_data["first_name"],
                "last_name": serializer.validated_data["last_name"],
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
