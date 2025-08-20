from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import ScopedRateThrottle

from .models import Cart
from .serializers import CartSerializer


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