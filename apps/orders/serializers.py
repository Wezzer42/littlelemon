from rest_framework import serializers
from .models import Order, OrderItem
from apps.menu.serializers import MenuItemSerializer
from django.contrib.auth.models import User
from apps.accounts.serializers import UserTinySerializer

        
class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "menuitem", "quantity", "unit_price", "price"]

class OrderSerializer(serializers.ModelSerializer):
    user = UserTinySerializer(read_only=True)
    delivery_crew = UserTinySerializer(read_only=True)
    delivery_crew_id = serializers.PrimaryKeyRelatedField(
        source="delivery_crew", queryset=User.objects.all(), write_only=True, required=False, allow_null=True
    )
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "delivery_crew",
            "delivery_crew_id",
            "status",
            "total",
            "date",
            "items",
            "shipping_address",
        ]
        read_only_fields = ["user", "total", "date"]