from django.test import TestCase
from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal

# Группы
MANAGER = "Manager"
DELIVERY = "Delivery crew"

def bearer_hdr(token: str):
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

class BaseSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        # группы
        cls.g_manager, _ = Group.objects.get_or_create(name=MANAGER)
        cls.g_delivery, _ = Group.objects.get_or_create(name=DELIVERY)

        # пользователи
        cls.admin = User.objects.create_superuser("admin", "a@a.a", "pass")
        cls.manager = User.objects.create_user("manager", password="pass")
        cls.delivery = User.objects.create_user("crew", password="pass")
        cls.customer = User.objects.create_user("cust", password="pass")

        cls.manager.groups.add(cls.g_manager)
        cls.delivery.groups.add(cls.g_delivery)

        # категории и меню
        from apps.menu.models import Category, MenuItem
        cls.cat = Category.objects.create(title="Main")
        cls.m1 = MenuItem.objects.create(
            title="Pizza", price=Decimal("12.50"),
            featured=False, category=cls.cat
        )
        cls.m2 = MenuItem.objects.create(
            title="Pasta", price=Decimal("10.00"),
            featured=True, category=cls.cat
        )

    def setUp(self):
        self.c = APIClient()

    # JWT login через Djoser: /auth/jwt/create/
    def jwt_access(self, username, password="pass") -> str:
        r = self.c.post(
            "/auth/jwt/create/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        data = r.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        return data["access"]

class ChecklistCourseraTests(BaseSetup):
    # Admin → add user to Manager
    def test_admin_can_assign_to_manager_group(self):
        t = self.jwt_access("admin", "pass")
        r = self.c.post(
            "/api/groups/manager/users",
            {"user_id": self.customer.id},
            format="json",
            **bearer_hdr(t)
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.content)
        self.assertTrue(
            User.objects.get(id=self.customer.id).groups.filter(name=MANAGER).exists()
        )

    # Admin → list manager group
    def test_admin_can_list_manager_group(self):
        t = self.jwt_access("admin")
        r = self.c.get("/api/groups/manager/users", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        self.assertTrue(any(u["username"] == "manager" for u in r.json()))

    # Admin → add menu items
    def test_admin_can_add_menu_items(self):
        t = self.jwt_access("admin")
        payload = {
            "title": "Salad",
            "price": "7.00",
            "featured": False,
            "category": "salad",
            "inventory": 3,
        }
        r = self.c.post("/api/menu-items", payload, format="multipart", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.content)

    # Admin → add categories
    def test_admin_can_add_categories(self):
        t = self.jwt_access("admin")
        r = self.c.post("/api/categories", {"title": "Desserts"}, format="json", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.content)

    # Manager login (JWT)
    def test_manager_login_jwt(self):
        r = self.c.post(
            "/auth/jwt/create/",
            {"username": "manager", "password": "pass"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        self.assertIn("access", r.json())
        self.assertIn("refresh", r.json())

    # Manager → update featured
    def test_manager_can_patch_featured(self):
        t = self.jwt_access("manager")
        r = self.c.patch(
            f"/api/menu-items/{self.m1.id}",
            {"featured": True},
            format="json",
            **bearer_hdr(t)
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        from apps.menu.models import MenuItem
        self.assertTrue(MenuItem.objects.get(id=self.m1.id).featured)

    # Manager → assign users to delivery crew
    def test_manager_can_assign_delivery_crew(self):
        t = self.jwt_access("manager")
        r = self.c.post(
            "/api/groups/delivery-crew/users",
            {"user_id": self.customer.id},
            format="json",
            **bearer_hdr(t)
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.content)
        self.assertTrue(
            User.objects.get(id=self.customer.id).groups.filter(name=DELIVERY).exists()
        )

    # Manager → assign order to delivery crew (PATCH per spec)
    def test_manager_can_assign_order(self):
        from apps.orders.models import Order
        o = Order.objects.create(user=self.customer, status=0, total=Decimal("0"))
        t = self.jwt_access("manager")
        r = self.c.patch(
            f"/api/orders/{o.id}",
            {"delivery_crew_id": self.delivery.id, "status": 0},
            format="json",
            **bearer_hdr(t)
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        self.assertEqual(r.json()["delivery_crew"]["id"], self.delivery.id)

    # Delivery → view assigned
    def test_delivery_can_view_assigned(self):
        from apps.orders.models import Order
        a = Order.objects.create(user=self.customer, delivery_crew=self.delivery, status=0, total=0)
        _ = Order.objects.create(user=self.customer, delivery_crew=None, status=0, total=0)
        t = self.jwt_access("crew")
        r = self.c.get("/api/orders", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        data = r.json()
        items = data["results"] if isinstance(data, dict) and "results" in data else data
        ids = [o["id"] for o in items]
        self.assertIn(a.id, ids)

    # Delivery → mark delivered
    def test_delivery_can_patch_status(self):
        from apps.orders.models import Order
        o = Order.objects.create(user=self.customer, delivery_crew=self.delivery, status=0, total=0)
        t = self.jwt_access("crew")
        r = self.c.patch(f"/api/orders/{o.id}", {"status": 1}, format="json", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        self.assertEqual(r.json()["status"], 1)

    # Customer → register (Djoser users)
    def test_customer_can_register(self):
        r = self.c.post(
            "/auth/users/",
            {"username": "newcust", "password": "Secret123!", "email": "nsda@nss.ns"},
            format="json",
        )
        self.assertIn(r.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK), msg=r.content)

    # Customer → login (JWT)
    def test_customer_can_login(self):
        r = self.c.post(
            "/auth/jwt/create/",
            {"username": "cust", "password": "pass"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        self.assertIn("access", r.json())

    # Customer → categories
    def test_customer_can_browse_categories(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/categories", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)

    # Customer → menu items
    def test_customer_can_browse_menu_items(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/menu-items", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
        data = r.json()
        items = data["results"] if isinstance(data, dict) and "results" in data else data
        titles = [i["title"] for i in items]
        self.assertIn("Pizza", titles)

    # Customer → search by category (поиск по названию категории)
    def test_customer_can_filter_by_category(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/menu-items", {"search": "main"}, **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)

    # Customer → pagination
    def test_customer_can_paginate(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/menu-items", {"page": 1}, **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)

    # Customer → ordering by price
    def test_customer_can_order_by_price(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/menu-items", {"ordering": "-price"}, **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)

    # Customer → add to cart (поддержим поле "menuitem")
    def test_customer_can_add_to_cart(self):
        t = self.jwt_access("cust")
        r = self.c.post(
            "/api/cart/menu-items",
            {"menuitem": self.m1.id, "quantity": 2},
            format="json",
            **bearer_hdr(t),
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, msg=r.content)

    # Customer → view cart
    def test_customer_can_view_cart(self):
        from apps.cart.models import Cart
        Cart.objects.create(
            user=self.customer, menuitem=self.m1, quantity=1,
            unit_price=self.m1.price, price=self.m1.price
        )
        t = self.jwt_access("cust")
        r = self.c.get("/api/cart/menu-items", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)

    # Customer → place order (alias /api/cart/orders)
    def test_customer_can_place_order(self):
        from apps.cart.models import Cart
        Cart.objects.create(
            user=self.customer, menuitem=self.m1, quantity=2,
            unit_price=self.m1.price, price=self.m1.price * 2
        )
        t = self.jwt_access("cust")
        r = self.c.post("/api/cart/orders", {"date": "2022-11-16"}, format="json", **bearer_hdr(t))
        self.assertIn(r.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK), msg=r.content)

    # Customer → view own orders (alias)
    def test_customer_can_browse_own_orders(self):
        t = self.jwt_access("cust")
        r = self.c.get("/api/cart/orders", **bearer_hdr(t))
        self.assertEqual(r.status_code, status.HTTP_200_OK, msg=r.content)
