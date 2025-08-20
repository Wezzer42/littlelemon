from rest_framework import serializers
from .models import MenuItem, Category


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