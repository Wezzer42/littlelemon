from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.orders.serializers import UserTinySerializer

from .permissions import IsManager
# Create your views here.

MANAGER = "Manager"
DELIVERY = "Delivery crew"

def derive_role(u) -> str:
    if u.is_superuser:
        return "admin"
    if u.is_staff or u.groups.filter(name=MANAGER).exists():
        return "manager"
    if u.groups.filter(name=DELIVERY).exists():
        return "delivery"
    return "user"

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    return Response({
        "id": u.id,
        "username": u.username,
        "email": u.email
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_role(request):
    return Response({"role": derive_role(request.user)})

class ManagerUsersView(APIView):
    """
    GET  /api/groups/manager/users        -> list managers
    POST /api/groups/manager/users        -> { "user_id": <int> } add to Manager
    """
    def get_permissions(self):
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

    def get(self, request):
        managers = User.objects.filter(groups__name="Manager")
        return Response(UserTinySerializer(managers, many=True).data)

    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=400)
        user = get_object_or_404(User, pk=user_id)
        group, _ = Group.objects.get_or_create(name="Manager")
        group.user_set.add(user)
        return Response(UserTinySerializer(user).data, status=201)


class ManagerUserDetailView(APIView):
    """
    DELETE /api/groups/manager/users/{userId}
    """
    def get_permissions(self):
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

    def delete(self, request, user_id):
        user = User.objects.filter(pk=user_id, groups__name="Manager").first()
        if not user:
            return Response({"detail": "Not found"}, status=404)
        group = Group.objects.get(name="Manager")
        group.user_set.remove(user)
        return Response(status=200)


class DeliveryCrewUsersView(APIView):
    """
    GET  /api/groups/delivery-crew/users  -> list delivery crew
    POST /api/groups/delivery-crew/users  -> { "user_id": <int> } add to crew
    """
    def get_permissions(self):
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

    def get(self, request):
        crew = User.objects.filter(groups__name="Delivery crew")
        return Response(UserTinySerializer(crew, many=True).data)

    def post(self, request):
        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"detail": "user_id is required"}, status=400)
        user = get_object_or_404(User, pk=user_id)
        group, _ = Group.objects.get_or_create(name="Delivery crew")
        group.user_set.add(user)
        return Response(UserTinySerializer(user).data, status=201)


class DeliveryCrewUserDetailView(APIView):
    """
    DELETE /api/groups/delivery-crew/users/{userId}
    """
    def get_permissions(self):
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

    def delete(self, request, user_id):
        user = User.objects.filter(pk=user_id, groups__name="Delivery crew").first()
        if not user:
            return Response({"detail": "Not found"}, status=404)
        group = Group.objects.get(name="Delivery crew")
        group.user_set.remove(user)
        return Response(status=200)