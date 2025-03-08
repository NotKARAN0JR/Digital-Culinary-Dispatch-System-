import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.config = {
            'dbname': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT')
        }

    @contextmanager
    def get_cursor(self):
        conn = psycopg2.connect(**self.config)
        try:
            yield conn.cursor(cursor_factory=RealDictCursor)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

class DatabaseOperations:
    def __init__(self):
        self.db = DatabaseConnection()

    # Customer operations
    def create_customer(self, name, phone, address, email, password_hash):
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO customers (name, phone, address, email, password_hash)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING customer_id
            """, (name, phone, address, email, password_hash))
            return cur.fetchone()['customer_id']

    def get_customer(self, email):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM customers WHERE email = %s", (email,))
            return cur.fetchone()

    # Restaurant operations
    def get_restaurants(self):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM restaurants WHERE is_active = true")
            return cur.fetchall()

    def get_menu_items(self, restaurant_id):
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT * FROM menu_items 
                WHERE restaurant_id = %s AND is_available = true
            """, (restaurant_id,))
            return cur.fetchall()

    # Order operations
    def create_order(self, customer_id, restaurant_id, total_amount, items):
        with self.db.get_cursor() as cur:
            # Create order
            cur.execute("""
                INSERT INTO orders (customer_id, restaurant_id, total_amount)
                VALUES (%s, %s, %s)
                RETURNING order_id
            """, (customer_id, restaurant_id, total_amount))
            order_id = cur.fetchone()['order_id']

            # Add order items
            for item in items:
                cur.execute("""
                    INSERT INTO order_items (order_id, menu_item_id, quantity, item_price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, item['menu_item_id'], item['quantity'], item['price']))

            return order_id

    def get_customer_orders(self, customer_id):
        with self.db.get_cursor() as cur:
            cur.execute("""
                SELECT o.*, r.name as restaurant_name,
                       d.status as delivery_status,
                       dp.name as delivery_person_name
                FROM orders o
                JOIN restaurants r ON o.restaurant_id = r.restaurant_id
                LEFT JOIN deliveries d ON o.order_id = d.order_id
                LEFT JOIN delivery_persons dp ON d.delivery_person_id = dp.delivery_person_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC
            """, (customer_id,))
            return cur.fetchall()

    # Review operations
    def create_review(self, order_id, customer_id, restaurant_id, rating, comments):
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO reviews (order_id, customer_id, restaurant_id, rating, comments)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING review_id
            """, (order_id, customer_id, restaurant_id, rating, comments))
            return cur.fetchone()['review_id']

    # Payment operations
    def create_payment(self, order_id, amount, payment_method):
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO payments (order_id, amount, payment_method)
                VALUES (%s, %s, %s)
                RETURNING payment_id
            """, (order_id, amount, payment_method))
            return cur.fetchone()['payment_id']

    # Delivery operations
    def assign_delivery(self, order_id, delivery_person_id):
        with self.db.get_cursor() as cur:
            cur.execute("""
                INSERT INTO deliveries (order_id, delivery_person_id)
                VALUES (%s, %s)
                RETURNING delivery_id
            """, (order_id, delivery_person_id))
            return cur.fetchone()['delivery_id']

    def update_delivery_status(self, delivery_id, status):
        with self.db.get_cursor() as cur:
            cur.execute("""
                UPDATE deliveries
                SET status = %s,
                    delivered_time = CASE WHEN %s = 'delivered' THEN CURRENT_TIMESTAMP ELSE delivered_time END
                WHERE delivery_id = %s
            """, (status, status, delivery_id))