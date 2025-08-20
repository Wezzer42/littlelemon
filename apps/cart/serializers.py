from rest_framework import serializers
from .models import MenuItem, Cart
from apps.menu.serializers import MenuItemSerializer


class CartSerializer(serializers.ModelSerializer):
    # READ: nested
    menuitem = MenuItemSerializer(read_only=True)

    # WRITE: принимаем и menuitem_id, и menuitem (как alias)
    menuitem_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Cart
        fields = ["id", "menuitem", "menuitem_id", "quantity", "unit_price", "price", "user"]
        read_only_fields = ["unit_price", "price", "user", "menuitem"]

    def validate(self, attrs):
        # достаём id из любого ключа
        incoming = self.initial_data or {}
        mid = incoming.get("menuitem_id") or incoming.get("menuitem")
        if not mid:
            raise serializers.ValidationError({"menuitem": "Provide menuitem or menuitem_id"})

        try:
            mi = MenuItem.objects.select_related("category").get(pk=mid)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError({"menuitem_id": "Invalid menuitem_id"})

        qty = int(incoming.get("quantity") or attrs.get("quantity") or 0)
        if qty <= 0:
            raise serializers.ValidationError({"quantity": "Must be > 0"})

        # заполняем вычисляемые поля в attrs
        attrs["menuitem"] = mi
        attrs["unit_price"] = mi.price
        attrs["price"] = mi.price * qty
        attrs["quantity"] = qty
        return attrs

    def create(self, validated):
        validated["user"] = self.context["request"].user
        # menuitem/quantity/unit_price/price уже проставлены в validate()
        return super().create(validated)