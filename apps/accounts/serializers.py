from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["address_line1", "address_line2", "city", "postal_code", "phone"]
        
class UserTinySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]