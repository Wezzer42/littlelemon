# LittleLemonAPI/urls.py
from django.urls import path
from .views import (
    CategoriesView, MenuItemsView,
    MenuItemDetailView
)

urlpatterns = [
    path("categories", CategoriesView.as_view()),          # ← /api/categories
    path("menu-items", MenuItemsView.as_view()),
    path("menu-items/<int:pk>", MenuItemDetailView.as_view()),
]
