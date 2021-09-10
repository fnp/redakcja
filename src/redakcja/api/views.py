from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from . import serializers


class MeView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserSerializer

    def get_object(self):
        return self.request.user
