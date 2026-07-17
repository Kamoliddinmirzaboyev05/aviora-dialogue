from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import ChangePasswordSerializer, EmailTokenObtainPairSerializer
from apps.workspaces.serializers import MembershipSerializer
from apps.workspaces.models import WorkspaceMembership


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Parol muvaffaqiyatli yangilandi."})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = WorkspaceMembership.objects.select_related("workspace").filter(user=request.user, is_active=True)
        return Response(
            {
                "user": {
                    "id": str(request.user.id),
                    "email": request.user.email,
                    "full_name": request.user.full_name,
                    "is_staff": request.user.is_staff,
                    "is_superuser": request.user.is_superuser,
                },
                "memberships": MembershipSerializer(memberships, many=True).data,
            }
        )
