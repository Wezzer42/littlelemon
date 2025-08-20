from rest_framework import permissions, generics
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle

from .models import Order, OrderItem
from apps.cart.models import Cart
from .serializers import OrderSerializer
from apps.accounts.permissions import in_group

# Create your views here.
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