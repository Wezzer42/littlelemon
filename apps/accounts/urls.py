# LittleLemonAPI/urls.py
from django.urls import path
from .views import (
    ManagerUsersView, ManagerUserDetailView,
    DeliveryCrewUsersView, DeliveryCrewUserDetailView, me, me_role
)

urlpatterns = [
    path("groups/manager/users", ManagerUsersView.as_view()),
    path("groups/manager/users/<int:user_id>", ManagerUserDetailView.as_view()),
    path("groups/delivery-crew/users", DeliveryCrewUsersView.as_view()),
    path("groups/delivery-crew/users/<int:user_id>", DeliveryCrewUserDetailView.as_view()),
    path("me", me),
    path("me/role", me_role),
]
