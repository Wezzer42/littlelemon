from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import permissions, generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser, FormParser

from .models import MenuItem, Cart, Order, OrderItem,Category
from .serializers import (
    MenuItemSerializer,
    CartSerializer,
    OrderSerializer,
    UserTinySerializer,
    CategorySerializer,
)
from .permissions import IsManager, in_group

class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [permissions.IsAuthenticated()]  # на листинги для групп пусть будет auth
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    parser_classes = (MultiPartParser, FormParser, )

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category", "featured", "price"]  # category = id
    search_fields   = ["title", "category__title"]
    ordering_fields = ["price", "title", "id"]

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [permissions.AllowAny()]
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]
    
class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.select_related("category").all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [permissions.AllowAny()]
        if self.request.user and self.request.user.is_superuser:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsManager()]

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


class CartView(APIView):
    """
    /api/cart/menu-items  (Customer only)
      GET    -> list current user's cart
      POST   -> add item  { menuitem_id, quantity }
      DELETE -> clear current user's cart
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "cart"
    throttle_classes = [ScopedRateThrottle]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        ser = CartSerializer(items, many=True)
        return Response(ser.data, status=200)

    def post(self, request):
        ser = CartSerializer(data=request.data, context={"request": request})
        if ser.is_valid():
            item = ser.save()
            return Response(CartSerializer(item).data, status=201)
        return Response(ser.errors, status=400)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=200)


class OrdersView(generics.ListCreateAPIView):
    """
    /api/orders
      GET:
        - Manager      -> all orders
        - Delivery crew-> orders assigned to them
        - Customer     -> their orders
      POST (Customer):
        - Create order from user's cart, move items to OrderItems, clear cart
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "orders"
    throttle_classes = [ScopedRateThrottle]

    filterset_fields = ["status", "user", "delivery_crew"]
    ordering_fields = ["date", "total", "status", "id"]
    ordering = ["-date"]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.all().select_related("user", "delivery_crew").prefetch_related("items__menuitem")
        if in_group(user, "Manager"):
            return qs
        if in_group(user, "Delivery crew"):
            return qs.filter(delivery_crew=user)
        return qs.filter(user=user)

    def create(self, request, *args, **kwargs):
        if in_group(request.user, "Manager") or in_group(request.user, "Delivery crew"):
            return Response({"detail": "Forbidden"}, status=403)

        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        order = Order.objects.create(user=request.user, status=0, total=0)
        total = 0
        bulk = []
        for c in cart_items:
            total += c.price
            bulk.append(OrderItem(
                order=order,
                menuitem=c.menuitem,
                quantity=c.quantity,
                unit_price=c.unit_price,
                price=c.price,
            ))
        OrderItem.objects.bulk_create(bulk)
        order.total = total
        order.save()
        cart_items.delete()

        return Response(OrderSerializer(order).data, status=201)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    /api/orders/{orderId}
      GET:
        - Manager      -> any
        - Delivery crew-> only if assigned
        - Customer     -> only own order (else 404)
      PUT/PATCH:
        - Manager      -> can assign delivery_crew_id, set status 0/1
        - Delivery crew-> PATCH status 0/1 only (cannot reassign)
        - Customer     -> forbidden
      DELETE:
        - Manager only
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "orders"
    throttle_classes = [ScopedRateThrottle]

    def get_queryset(self):
        user = self.request.user
        qs = Order.objects.all().select_related("user", "delivery_crew").prefetch_related("items__menuitem")
        if in_group(user, "Manager"):
            return qs
        if in_group(user, "Delivery crew"):
            return qs.filter(delivery_crew=user)
        return qs.filter(user=user)

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        data = request.data

        if in_group(request.user, "Manager"):
            allowed = {}
            if "delivery_crew_id" in data:
                allowed["delivery_crew_id"] = data.get("delivery_crew_id")
            if "status" in data:
                status_val = int(data.get("status"))
                if status_val not in (0, 1):
                    return Response({"detail": "status must be 0 or 1"}, status=400)
                allowed["status"] = status_val
            ser = self.get_serializer(order, data=allowed, partial=True)
            ser.is_valid(raise_exception=True)
            self.perform_update(ser)
            return Response(ser.data, status=200)

        if in_group(request.user, "Delivery crew"):
            if request.method == "PUT":
                return Response({"detail": "Use PATCH for status update"}, status=400)
            if order.delivery_crew_id != request.user.id:
                return Response({"detail": "Forbidden"}, status=403)
            if "status" not in data:
                return Response({"detail": "status is required"}, status=400)
            status_val = int(data.get("status"))
            if status_val not in (0, 1):
                return Response({"detail": "status must be 0 or 1"}, status=400)
            order.status = status_val
            order.save()
            return Response(self.get_serializer(order).data, status=200)

        return Response({"detail": "Forbidden"}, status=403)

    def destroy(self, request, *args, **kwargs):
        if not in_group(request.user, "Manager"):
            return Response({"detail": "Forbidden"}, status=403)
        return super().destroy(request, *args, **kwargs)
