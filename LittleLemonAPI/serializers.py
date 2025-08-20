from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem, User, Category, Profile

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True, required=False)
    category    = CategorySerializer(read_only=True)
    image       = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model  = MenuItem
        fields = ["id", "title", "price", "featured", "category", "category_id", "image"]

    def _apply_category(self, validated):
        cid = (self.initial_data or {}).get("category_id")
        if cid is not None:
            try:
                validated["category"] = Category.objects.get(pk=cid)
            except Category.DoesNotExist:
                raise serializers.ValidationError({"category_id": "Invalid category_id"})
        return validated

    def create(self, validated):
        validated = self._apply_category(validated)
        return super().create(validated)

    def update(self, instance, validated):
        validated = self._apply_category(validated)
        return super().update(instance, validated)
        
class UserTinySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
        
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

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["address_line1", "address_line2", "city", "postal_code", "phone"]