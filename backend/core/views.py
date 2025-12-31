from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import RegisterSerializer
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer

class RegisterView(APIView):
    """
    Register a new user.
    """

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        auth=[], # no authentication required
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description="User successfully registered",
                response={
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            ),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Logout a user.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                description="User successfully logged out",
                response={
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
            ),
            401: OpenApiResponse(
                description="Authentication credentials were not provided"
            ),
        },
    )
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "User logged out"}, status=status.HTTP_200_OK)


class CustomObtainAuthToken(ObtainAuthToken):
    """
    Obtain an authentication token for a user.
    """
    @extend_schema(
        request=AuthTokenSerializer,
        responses={
            200: OpenApiResponse(
                description="Authentication token obtained",
                response={"type": "object", "properties": {"token": {"type": "string"}}},
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)