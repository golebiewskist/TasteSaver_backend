from rest_framework import generics
from rest_framework.permissions import AllowAny
from accounts.models import CustomUser
from accounts.serializers import  RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer




