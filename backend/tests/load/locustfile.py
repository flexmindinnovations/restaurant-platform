import random
import uuid

from locust import HttpUser, between, task


class RestaurantPlatformUser(HttpUser):
    # Wait between 1 and 3 seconds between tasks
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user is spawned. Registers and logs in the user."""
        self.auth_headers = {}
        self.restaurant_ids = []
        self.placed_order_ids = []
        self.menu_item_ids = {}  # restaurant_id -> list of menu_item_ids

        self.email = f"loaduser_{uuid.uuid4().hex[:10]}@example.com"
        self.password = "StrongPass123!"

        # 1. Register a new customer account
        register_payload = {
            "email": self.email,
            "password": self.password,
            "phone_number": "+15555555555",
            "roles": ["CUSTOMER"],
        }

        with self.client.post("/api/v1/auth/register", json=register_payload, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            else:
                response.failure(f"Registration failed with status code {response.status_code}: {response.text}")
                return

        # 2. Login to get access token
        login_payload = {"email": self.email, "password": self.password}
        with self.client.post("/api/v1/auth/login", json=login_payload, catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json().get("data", {})
                    token = data.get("access_token")
                    if token:
                        self.auth_headers = {"Authorization": f"Bearer {token}"}
                        response.success()
                    else:
                        response.failure("Token not found in login response")
                except Exception as e:
                    response.failure(f"Failed to parse login response: {e}")
            else:
                response.failure(f"Login failed with status code {response.status_code}: {response.text}")

    @task(5)
    def browse_restaurants(self):
        """Browse the restaurant list."""
        if not self.auth_headers:
            return

        with self.client.get(
            "/api/v1/restaurants?skip=0&limit=10", headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    restaurants = response.json().get("data", {}).get("items", [])
                    self.restaurant_ids = [r["id"] for r in restaurants if "id" in r]
                    response.success()
                except Exception as e:
                    response.failure(f"Failed to parse restaurants list: {e}")
            else:
                response.failure(f"Failed to list restaurants: {response.status_code}")

    @task(4)
    def browse_menus(self):
        """Browse menus for a randomly selected restaurant."""
        if not self.auth_headers or not self.restaurant_ids:
            return

        restaurant_id = random.choice(self.restaurant_ids)
        with self.client.get(
            f"/api/v1/menus?restaurant_id={restaurant_id}", headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    menus = response.json().get("data", {}).get("items", [])
                    item_ids = []
                    for m in menus:
                        for cat in m.get("categories", []):
                            # In some schemas, categories have nested items, or we search for them
                            # Let's also check if we can query menu items via search or direct fields
                            pass

                    # If direct nested list wasn't parsed, we fallback to searching menu items
                    if not item_ids:
                        self._fetch_items_via_search(restaurant_id)
                    else:
                        self.menu_item_ids[restaurant_id] = item_ids

                    response.success()
                except Exception as e:
                    response.failure(f"Failed to parse menus: {e}")
            else:
                response.failure(f"Failed to get menus: {response.status_code}")

    def _fetch_items_via_search(self, restaurant_id):
        """Helper to find menu items for a restaurant if not nested in menu query."""
        with self.client.get(
            f"/api/v1/menus/search?restaurant_id={restaurant_id}&q=a", headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    items = response.json().get("data", {}).get("items", [])
                    self.menu_item_ids[restaurant_id] = [i["id"] for i in items if "id" in i]
                    response.success()
                except Exception:
                    pass

    @task(3)
    def add_item_to_cart(self):
        """Add a customized item to the cart."""
        if not self.auth_headers or not self.menu_item_ids:
            return

        # Select a restaurant that has items loaded
        active_restaurants = [rid for rid, items in self.menu_item_ids.items() if items]
        if not active_restaurants:
            return

        restaurant_id = random.choice(active_restaurants)
        item_id = random.choice(self.menu_item_ids[restaurant_id])

        cart_payload = {
            "menu_item_id": item_id,
            "quantity": random.randint(1, 3),
            "special_instructions": random.choice(["No onions", "Extra spicy", "Sauce on the side", ""]),
        }

        with self.client.post(
            "/api/v1/checkout/cart/items", json=cart_payload, headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Failed to add item to cart: {response.status_code} - {response.text}")

    @task(2)
    def checkout_and_place_order(self):
        """Place an order for items in the cart."""
        if not self.auth_headers:
            return

        order_payload = {
            "delivery_address_street": "123 Main St",
            "delivery_address_city": "Metropolis",
            "delivery_address_state": "NY",
            "delivery_address_postal_code": "10001",
            "delivery_address_country": "USA",
            "tip_amount": "5.00",
            "delivery_notes": "Leave at front door",
        }

        with self.client.post(
            "/api/v1/checkout/place-order", json=order_payload, headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code in [200, 201]:
                try:
                    order_id = response.json().get("data", {}).get("order_id")
                    if order_id:
                        self.placed_order_ids.append(order_id)
                        response.success()
                    else:
                        response.failure("Order ID missing in checkout response")
                except Exception as e:
                    response.failure(f"Failed to parse order response: {e}")
            # If cart is empty, this might return 400, which is normal for users who haven't added items yet
            elif response.status_code == 400:
                response.success()
            else:
                response.failure(f"Checkout failed: {response.status_code} - {response.text}")

    @task(3)
    def poll_tracking_maps(self):
        """Poll the delivery tracking map status for any placed orders."""
        if not self.auth_headers or not self.placed_order_ids:
            return

        order_id = random.choice(self.placed_order_ids)
        with self.client.get(
            f"/api/v1/delivery-assignments/orders/{order_id}", headers=self.auth_headers, catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Order might not have a delivery assignment/partner assigned yet, which is expected
                response.success()
            else:
                response.failure(f"Error polling delivery details: {response.status_code} - {response.text}")
