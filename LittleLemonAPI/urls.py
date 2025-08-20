# LittleLemonAPI/urls.py
from django.urls import path
from .views import (
    CategoriesView, MenuItemsView,
    ManagerUsersView, ManagerUserDetailView,
    DeliveryCrewUsersView, DeliveryCrewUserDetailView,
    CartView, OrdersView, OrderDetailView, MenuItemDetailView
)
from .views_me import me

urlpatterns = [
    path("categories", CategoriesView.as_view()),          # ← /api/categories
    path("menu-items", MenuItemsView.as_view()),
    path("menu-items/<int:pk>", MenuItemDetailView.as_view()),
    # groups
    path("groups/manager/users", ManagerUsersView.as_view()),
    path("groups/manager/users/<int:user_id>", ManagerUserDetailView.as_view()),
    path("groups/delivery-crew/users", DeliveryCrewUsersView.as_view()),
    path("groups/delivery-crew/users/<int:user_id>", DeliveryCrewUserDetailView.as_view()),
    # cart
    path("cart/menu-items", CartView.as_view()),
    # orders
    path("orders", OrdersView.as_view()),
    path("orders/<int:pk>", OrderDetailView.as_view()),
    # aliases expected by the checklist:
    path("cart/orders", OrdersView.as_view()),
    path("me", me),
]
