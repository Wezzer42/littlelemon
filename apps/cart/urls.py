# LittleLemonAPI/urls.py
from django.urls import path
from .views import CartView


urlpatterns = [
    path("cart/menu-items", CartView.as_view()),
]
