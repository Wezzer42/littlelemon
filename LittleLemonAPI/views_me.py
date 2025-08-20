from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

MANAGER = "Manager"
DELIVERY = "Delivery crew"

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    u = request.user
    is_manager = u.is_superuser or u.is_staff or u.groups.filter(name=MANAGER).exists()
    is_delivery = u.groups.filter(name=DELIVERY).exists()
    return Response({
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "is_manager": is_manager,
        "is_delivery": is_delivery,
        "is_staff": u.is_staff,
        "is_superuser": u.is_superuser,
    })
