from decimal import Decimal

from django.contrib.auth.models import User, Group
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.core.cache import cache

from LittleLemonAPI.models import MenuItem, Cart, Order, OrderItem, Category


# ------------------------------
# MenuItems CRUD & permissions
# ------------------------------
class MenuItemsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Groups
        cls.manager_group, _ = Group.objects.get_or_create(name="Manager")
        cls.delivery_group, _ = Group.objects.get_or_create(name="Delivery crew")

        # Users
        cls.customer = User.objects.create_user(username="cust", password="pass")
        cls.delivery = User.objects.create_user(username="crew", password="pass")
        cls.manager = User.objects.create_user(username="boss", password="pass")
        cls.delivery.groups.add(cls.delivery_group)
        cls.manager.groups.add(cls.manager_group)

        # Categories
        cls.cat_main = Category.objects.create(title="main")
        cls.cat_salad = Category.objects.create(title="salad")

        # Seed data
        cls.item = MenuItem.objects.create(
            title="Pizza", price=Decimal("12.50"), featured=False, category=cls.cat_main, inventory=10
        )
        cls.list_url = "/api/menu-items"
        cls.detail_url = f"/api/menu-items/{cls.item.id}"

    def setUp(self):
        self.client = APIClient()

    # -------- Customers & Delivery crew: GET allowed --------
    def test_customer_get_list_200(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delivery_get_list_200(self):
        self.client.force_authenticate(self.delivery)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_customer_get_detail_200(self):
        self.client.force_authenticate(self.customer)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_delivery_get_detail_200(self):
        self.client.force_authenticate(self.delivery)
        resp = self.client.get(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # -------- Customers & Delivery crew: write -> 403 --------
    def test_customer_post_403(self):
        self.client.force_authenticate(self.customer)
        payload = {"title": "Burger", "price": "9.99", "featured": False, "category_id": self.cat_main.id, "inventory": 5}
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delivery_delete_403(self):
        self.client.force_authenticate(self.delivery)
        resp = self.client.delete(self.detail_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_put_patch_403(self):
        self.client.force_authenticate(self.customer)
        resp_put = self.client.put(
            self.detail_url,
            {"title": "New", "price": "10.00", "featured": False, "category_id": self.cat_main.id, "inventory": 7},
            format="json",
        )
        resp_patch = self.client.patch(self.detail_url, {"price": "10.00"}, format="json")
        self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp_patch.status_code, status.HTTP_403_FORBIDDEN)

    # -------- Manager: full access --------
    def test_manager_get_list_200(self):
        self.client.force_authenticate(self.manager)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_manager_post_201(self):
        self.client.force_authenticate(self.manager)
        payload = {"title": "Pasta", "price": "15.00", "featured": True, "category_id": self.cat_main.id, "inventory": 8}
        resp = self.client.post(self.list_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MenuItem.objects.filter(title="Pasta").exists())

    def test_manager_put_patch_delete(self):
        self.client.force_authenticate(self.manager)
        # PUT
        put_payload = {
            "title": "Pizza Special",
            "price": "13.00",
            "featured": True,
            "category_id": self.cat_main.id,
            "inventory": 11,
        }
        resp_put = self.client.put(self.detail_url, put_payload, format="json")
        self.assertEqual(resp_put.status_code, status.HTTP_200_OK)
        # PATCH
        resp_patch = self.client.patch(self.detail_url, {"price": "14.00"}, format="json")
        self.assertEqual(resp_patch.status_code, status.HTTP_200_OK)
        # DELETE
        resp_del = self.client.delete(self.detail_url)
        self.assertIn(resp_del.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])


# ------------------------------
# Group management endpoints
# ------------------------------
class GroupEndpointsTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager_group, _ = Group.objects.get_or_create(name="Manager")
        cls.delivery_group, _ = Group.objects.get_or_create(name="Delivery crew")

        cls.user_plain = User.objects.create_user(username="plain", password="pass")
        cls.user_manager = User.objects.create_user(username="boss", password="pass")
        cls.user_delivery = User.objects.create_user(username="crew", password="pass")

        cls.user_manager.groups.add(cls.manager_group)
        cls.user_delivery.groups.add(cls.delivery_group)

        cls.managers_url = "/api/groups/manager/users"
        cls.manager_detail = lambda user_id: f"/api/groups/manager/users/{user_id}"

        cls.delivery_url = "/api/groups/delivery-crew/users"
        cls.delivery_detail = lambda user_id: f"/api/groups/delivery-crew/users/{user_id}"

    def setUp(self):
        self.client = APIClient()

    # ---------- 401/403 ----------
    def test_unauthenticated_get_managers_401(self):
        resp = self.client.get(self.managers_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_manager_get_managers_403(self):
        self.client.force_authenticate(self.user_plain)
        resp = self.client.get(self.managers_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- Managers list ----------
    def test_manager_get_managers_200(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.get(self.managers_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u["username"] == "boss" for u in resp.json()))

    # ---------- Managers POST add ----------
    def test_manager_post_add_manager_201(self):
        self.client.force_authenticate(self.user_manager)
        payload = {"user_id": self.user_plain.id}
        resp = self.client.post(self.managers_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.user_plain.groups.filter(name="Manager").exists())

    def test_manager_post_add_manager_400_when_missing_user_id(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.post(self.managers_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_manager_post_add_manager_403(self):
        self.client.force_authenticate(self.user_plain)
        payload = {"user_id": self.user_delivery.id}
        resp = self.client.post(self.managers_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- Managers DELETE ----------
    def test_manager_delete_manager_200(self):
        self.user_plain.groups.add(self.manager_group)

        self.client.force_authenticate(self.user_manager)
        resp = self.client.delete(self.manager_detail(self.user_plain.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user_plain.groups.filter(name="Manager").exists())

    def test_manager_delete_manager_404_when_not_in_group(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.delete(self.manager_detail(self.user_plain.id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_non_manager_delete_manager_403(self):
        self.client.force_authenticate(self.user_plain)
        resp = self.client.delete(self.manager_detail(self.user_manager.id))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- Delivery crew list ----------
    def test_manager_get_delivery_200(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.get(self.delivery_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(any(u["username"] == "crew" for u in resp.json()))

    def test_non_manager_get_delivery_403(self):
        self.client.force_authenticate(self.user_plain)
        resp = self.client.get(self.delivery_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    # ---------- Delivery crew POST add ----------
    def test_manager_post_add_delivery_201(self):
        self.client.force_authenticate(self.user_manager)
        payload = {"user_id": self.user_plain.id}
        resp = self.client.post(self.delivery_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.user_plain.groups.filter(name="Delivery crew").exists())

    def test_manager_post_add_delivery_400_when_missing_user_id(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.post(self.delivery_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------- Delivery crew DELETE ----------
    def test_manager_delete_delivery_200(self):
        self.user_plain.groups.add(self.delivery_group)

        self.client.force_authenticate(self.user_manager)
        resp = self.client.delete(self.delivery_detail(self.user_plain.id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user_plain.groups.filter(name="Delivery crew").exists())

    def test_manager_delete_delivery_404_when_not_in_group(self):
        self.client.force_authenticate(self.user_manager)
        resp = self.client.delete(self.delivery_detail(self.user_plain.id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ------------------------------
# Cart tests
# ------------------------------
class CartTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username="alice", password="pass")
        cls.user2 = User.objects.create_user(username="bob", password="pass")

        cls.cat_main = Category.objects.create(title="main")

        cls.item1 = MenuItem.objects.create(
            title="Pizza", price=Decimal("12.50"), featured=False, category=cls.cat_main, inventory=10
        )
        cls.item2 = MenuItem.objects.create(
            title="Pasta", price=Decimal("10.00"), featured=False, category=cls.cat_main, inventory=7
        )

        cls.cart_url = "/api/cart/menu-items"

    def setUp(self):
        self.client = APIClient()

    # ---------- 401----------
    def test_unauthenticated_get_401(self):
        resp = self.client.get(self.cart_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_post_401(self):
        resp = self.client.post(self.cart_url, {"menuitem_id": self.item1.id, "quantity": 1}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_delete_401(self):
        resp = self.client.delete(self.cart_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # ---------- GET----------
    def test_get_returns_only_current_user_items(self):
        Cart.objects.create(
            user=self.user1,
            menuitem=self.item1,
            quantity=2,
            unit_price=self.item1.price,
            price=self.item1.price * 2,
        )
        Cart.objects.create(
            user=self.user2,
            menuitem=self.item2,
            quantity=1,
            unit_price=self.item2.price,
            price=self.item2.price * 1,
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.get(self.cart_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["menuitem"]["title"], "Pizza")
        self.assertEqual(Decimal(str(data[0]["price"])), Decimal("25.00"))

    # ---------- POST----------
    def test_post_adds_item_and_computes_prices(self):
        self.client.force_authenticate(self.user1)
        payload = {"menuitem_id": self.item1.id, "quantity": 3}
        resp = self.client.post(self.cart_url, payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body = resp.json()
        self.assertEqual(body["menuitem"]["title"], "Pizza")
        self.assertEqual(body["quantity"], 3)
        self.assertEqual(Decimal(str(body["unit_price"])), Decimal("12.50"))
        self.assertEqual(Decimal(str(body["price"])), Decimal("37.50"))

        created = Cart.objects.get(id=body["id"])
        self.assertEqual(created.user_id, self.user1.id)
        self.assertEqual(created.menuitem_id, self.item1.id)
        self.assertEqual(created.quantity, 3)
        self.assertEqual(created.unit_price, Decimal("12.50"))
        self.assertEqual(created.price, Decimal("37.50"))

    # ---------- DELETE ----------
    def test_delete_clears_only_current_user_cart(self):
        Cart.objects.create(
            user=self.user1,
            menuitem=self.item1,
            quantity=1,
            unit_price=self.item1.price,
            price=self.item1.price * 1,
        )
        Cart.objects.create(
            user=self.user1,
            menuitem=self.item2,
            quantity=2,
            unit_price=self.item2.price,
            price=self.item2.price * 2,
        )
        Cart.objects.create(
            user=self.user2,
            menuitem=self.item2,
            quantity=1,
            unit_price=self.item2.price,
            price=self.item2.price * 1,
        )

        self.client.force_authenticate(self.user1)
        resp = self.client.delete(self.cart_url)
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])

        self.assertEqual(Cart.objects.filter(user=self.user1).count(), 0)
        self.assertEqual(Cart.objects.filter(user=self.user2).count(), 1)


# ------------------------------
# Orders tests
# ------------------------------
class OrdersTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Groups
        cls.manager_group, _ = Group.objects.get_or_create(name="Manager")
        cls.delivery_group, _ = Group.objects.get_or_create(name="Delivery crew")

        # Users
        cls.customer1 = User.objects.create_user(username="cust1", password="pass")
        cls.customer2 = User.objects.create_user(username="cust2", password="pass")
        cls.manager = User.objects.create_user(username="boss", password="pass")
        cls.delivery = User.objects.create_user(username="crew", password="pass")
        cls.manager.groups.add(cls.manager_group)
        cls.delivery.groups.add(cls.delivery_group)

        # Categories
        cls.cat_main = Category.objects.create(title="main")

        # Menu
        cls.pizza = MenuItem.objects.create(title="Pizza", price=Decimal("12.50"), featured=False, category=cls.cat_main, inventory=10)
        cls.pasta = MenuItem.objects.create(title="Pasta", price=Decimal("10.00"), featured=False, category=cls.cat_main, inventory=8)

        # URLs
        cls.list_url = "/api/orders"

    def setUp(self):
        self.client = APIClient()

    # ------------------ 401 ------------------
    def test_unauthenticated_get_orders_401(self):
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_post_orders_401(self):
        resp = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------------------ Customer: POST creates order from cart & clears cart ------------------
    def test_customer_post_creates_order_from_cart_and_clears(self):
        # customer1 кладёт в корзину 2*Pizza + 1*Pasta
        Cart.objects.create(user=self.customer1, menuitem=self.pizza, quantity=2, unit_price=self.pizza.price, price=self.pizza.price * 2)
        Cart.objects.create(user=self.customer1, menuitem=self.pasta, quantity=1, unit_price=self.pasta.price, price=self.pasta.price * 1)

        self.client.force_authenticate(self.customer1)
        resp = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        body = resp.json()
        self.assertIn("id", body)
        self.assertEqual(Decimal(str(body["total"])), Decimal("35.00"))  # 2*12.50 + 1*10.00
        self.assertEqual(len(body["items"]), 2)

        # корзина очищена
        self.assertEqual(Cart.objects.filter(user=self.customer1).count(), 0)

    def test_customer_post_cart_empty_400(self):
        self.client.force_authenticate(self.customer1)
        resp = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Cart is empty", resp.json().get("detail", ""))

    # ------------------ Customer: GET list own, GET detail only own (else 404) ------------------
    def _make_order_for_user(self, user, assigned_to=None, total=Decimal("10.00")):
        order = Order.objects.create(user=user, delivery_crew=assigned_to, status=0, total=total)
        OrderItem.objects.create(order=order, menuitem=self.pasta, quantity=1, unit_price=self.pasta.price, price=self.pasta.price)
        return order

    def test_customer_get_list_only_own(self):
        o1 = self._make_order_for_user(self.customer1, None, Decimal("10.00"))
        _o2 = self._make_order_for_user(self.customer2, None, Decimal("12.50"))

        self.client.force_authenticate(self.customer1)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [o["id"] for o in resp.json()["results"]] if isinstance(resp.json(), dict) and "results" in resp.json() else [o["id"] for o in resp.json()]
        self.assertIn(o1.id, ids)
        self.assertNotIn(_o2.id, ids)

    def test_customer_get_other_users_order_404(self):
        other_order = self._make_order_for_user(self.customer2, None, Decimal("12.50"))
        self.client.force_authenticate(self.customer1)
        resp = self.client.get(f"{self.list_url}/{other_order.id}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # ------------------ Manager: GET all, assign delivery crew, set status, delete ------------------
    def test_manager_get_all_orders(self):
        o1 = self._make_order_for_user(self.customer1)
        o2 = self._make_order_for_user(self.customer2)

        self.client.force_authenticate(self.manager)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [o["id"] for o in resp.json()["results"]] if isinstance(resp.json(), dict) and "results" in resp.json() else [o["id"] for o in resp.json()]
        self.assertIn(o1.id, ids)
        self.assertIn(o2.id, ids)

    def test_manager_put_assign_delivery_and_status(self):
        order = self._make_order_for_user(self.customer1)
        self.client.force_authenticate(self.manager)

        # назначаем доставщика и ставим статус 0
        payload = {"delivery_crew_id": self.delivery.id, "status": 0}
        resp = self.client.put(f"{self.list_url}/{order.id}", payload, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        body = resp.json()
        self.assertIsNotNone(body["delivery_crew"])
        self.assertEqual(body["delivery_crew"]["id"], self.delivery.id)
        self.assertEqual(body["status"], 0)

        # меняем статус на 1
        resp2 = self.client.patch(f"{self.list_url}/{order.id}", {"status": 1}, format="json")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.json()["status"], 1)

    def test_manager_delete_order(self):
        order = self._make_order_for_user(self.customer1)
        self.client.force_authenticate(self.manager)
        resp = self.client.delete(f"{self.list_url}/{order.id}")
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        self.assertFalse(Order.objects.filter(id=order.id).exists())

    # ------------------ Delivery crew: GET assigned only, PATCH status only ------------------
    def test_delivery_get_only_assigned(self):
        assigned = self._make_order_for_user(self.customer1, assigned_to=self.delivery)
        not_assigned = self._make_order_for_user(self.customer2, assigned_to=None)

        self.client.force_authenticate(self.delivery)
        resp = self.client.get(self.list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [o["id"] for o in resp.json()["results"]] if isinstance(resp.json(), dict) and "results" in resp.json() else [o["id"] for o in resp.json()]
        self.assertIn(assigned.id, ids)
        self.assertNotIn(not_assigned.id, ids)

    def test_delivery_patch_status_only_when_assigned(self):
        order = self._make_order_for_user(self.customer1, assigned_to=self.delivery)

        self.client.force_authenticate(self.delivery)
        # не PATCH  — PUT должен вернуть 400 (требуется PATCH)
        resp_put = self.client.put(f"{self.list_url}/{order.id}", {"status": 1}, format="json")
        self.assertEqual(resp_put.status_code, status.HTTP_400_BAD_REQUEST)

        # PATCH корректный
        resp = self.client.patch(f"{self.list_url}/{order.id}", {"status": 1}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.json()["status"], 1)

    def test_delivery_patch_status_for_not_assigned_403(self):
        other = self._make_order_for_user(self.customer1, assigned_to=None)
        self.client.force_authenticate(self.delivery)
        resp = self.client.patch(f"{self.list_url}/{other.id}", {"status": 1}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delivery_patch_status_invalid_value_400(self):
        order = self._make_order_for_user(self.customer1, assigned_to=self.delivery)
        self.client.force_authenticate(self.delivery)
        resp = self.client.patch(f"{self.list_url}/{order.id}", {"status": 2}, format="json")  # допустимы только 0/1
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------ Forbidden updates for customers ------------------
    def test_customer_cannot_update_order_403(self):
        order = self._make_order_for_user(self.customer1)
        self.client.force_authenticate(self.customer1)
        resp_put = self.client.put(f"{self.list_url}/{order.id}", {"status": 1}, format="json")
        resp_patch = self.client.patch(f"{self.list_url}/{order.id}", {"status": 1}, format="json")
        self.assertEqual(resp_put.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(resp_patch.status_code, status.HTTP_403_FORBIDDEN)


# ------------------------------
# Search/Filter/Ordering tests for MenuItems
# ------------------------------
class MenuItemsFiltersTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat_main  = Category.objects.create(title="main")
        cls.cat_salad = Category.objects.create(title="salad")

        MenuItem.objects.create(title="Pizza Margherita", price="10.00", featured=False, category=cls.cat_main,  inventory=10)
        MenuItem.objects.create(title="Pizza Pepperoni",  price="12.00", featured=True,  category=cls.cat_main,  inventory=8)
        MenuItem.objects.create(title="Salad Greek",      price="7.50",  featured=False, category=cls.cat_salad, inventory=5)
        MenuItem.objects.create(title="Pasta Carbonara",  price="9.00",  featured=True,  category=cls.cat_main,  inventory=7)

    def setUp(self):
        self.client = APIClient()

    def test_search_and_filter_and_ordering(self):
        resp = self.client.get(
            "/api/menu-items",
            {"search": "Pizza", "category": self.cat_main.id, "ordering": "-price", "page_size": 2},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.json()
        results = data.get("results", data)
        titles = [r["title"] for r in results]
        self.assertIn("Pizza Pepperoni", titles)
        self.assertIn("Pizza Margherita", titles)


# ------------------------------
# Throttling
# ------------------------------
@override_settings(
    REST_FRAMEWORK={
        **__import__("littlelemon.settings").settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "orders": "3/min",
            "user": "100/day",
            "anon": "100/day",
        },
    }
)
class ThrottlingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="u", password="p")

    def setUp(self):
        # важный момент: обнуляем счётчики перед тестом
        cache.clear()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_orders_throttle_scope(self):
        # первые три — 200
        for _ in range(60):
            r = self.client.get("/api/orders")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
        # четвёртый — 429
        r = self.client.get("/api/orders")
        self.assertEqual(r.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
