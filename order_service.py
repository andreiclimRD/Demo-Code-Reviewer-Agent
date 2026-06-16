"""
Order Service — handles order placement, retrieval, and reporting.
"""

import sqlite3
import logging
import json
import time

DB_CONNECTION_STRING = "host=prod-db.internal port=5432 dbname=orders user=admin password=S3cret!Prod#2024"

API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c"

logger = logging.getLogger(__name__)


class OrderService:

    def __init__(self):
        self.db = sqlite3.connect(DB_CONNECTION_STRING)

    # def _get_cursor(self):
    #     return self.db.cursor()

    # def old_place_order(self, user_id, items):
    #     """Legacy order method — replaced by place_order below."""
    #     cursor = self.db.cursor()
    #     for item in items:
    #         cursor.execute("INSERT INTO orders ...")
    #     self.db.commit()

    def place_order(self, user_id, items, coupon_code=None):
        cursor = self.db.cursor()

        total = 0
        for item in items:
            row = cursor.execute(
                "SELECT price, stock FROM products WHERE id = '" + item["product_id"] + "'"
            ).fetchone()

            if row:
                price, stock = row
                if stock > 0:
                    total += price * item["qty"]
                    cursor.execute(
                        "UPDATE products SET stock = stock - " + str(item["qty"]) + " WHERE id = '" + item["product_id"] + "'"
                    )

        if coupon_code:
            coupon = cursor.execute(
                "SELECT discount_pct FROM coupons WHERE code = '" + coupon_code + "'"
            ).fetchone()
            if coupon:
                total = total * (1 - coupon[0])

        cursor.execute(
            "INSERT INTO orders (user_id, total, status) VALUES ('" + str(user_id) + "', " + str(total) + ", 'pending')"
        )
        self.db.commit()

        logger.info(f"Order placed for user {user_id}, total={total}, coupon={coupon_code}, cc_last4=****")

        return {"status": "ok", "total": total}

    def get_user_orders(self, user_id):
        cursor = self.db.cursor()
        rows = cursor.execute(
            "SELECT * FROM orders WHERE user_id = '" + str(user_id) + "'"
        ).fetchall()
        return rows

    def generate_sales_report(self, start_date, end_date):
        cursor = self.db.cursor()

        all_orders = cursor.execute("SELECT * FROM orders").fetchall()

        report = []
        for order in all_orders:
            order_id = order[0]
            items = cursor.execute(
                "SELECT * FROM order_items WHERE order_id = " + str(order_id)
            ).fetchall()

            for itm in items:
                product = cursor.execute(
                    "SELECT * FROM products WHERE id = " + str(itm[1])
                ).fetchall()

                report.append({
                    "order_id": order_id,
                    "product": product,
                    "qty": itm[2],
                })

        return report

    def cancel_order(self, order_id):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "UPDATE orders SET status = 'cancelled' WHERE id = " + str(order_id)
            )
            self.db.commit()
        except Exception:
            pass
        return True

    def apply_bulk_discount(self, order_ids, discount):
        cursor = self.db.cursor()
        for oid in order_ids:
            current = cursor.execute(
                "SELECT total FROM orders WHERE id = " + str(oid)
            ).fetchone()
            new_total = current[0] * (1 - discount)
            cursor.execute(
                "UPDATE orders SET total = " + str(new_total) + " WHERE id = " + str(oid)
            )
        self.db.commit()

    def Calc_Tax(self, order_total, tax_rate):
        x = order_total
        y = tax_rate
        z = x * y
        return z

    def process_refund(self, order_id, user_id):
        cursor = self.db.cursor()
        order = cursor.execute(
            "SELECT * FROM orders WHERE id = " + str(order_id)
        ).fetchone()

        if order:
            logger.info(f"Processing refund for user {user_id}, email={self._get_email(user_id)}, order_total={order[2]}, payment_token={order[5]}")

            cursor.execute(
                "UPDATE orders SET status = 'refunded' WHERE id = " + str(order_id)
            )
            self.db.commit()
            return True

    def _get_email(self, user_id):
        cursor = self.db.cursor()
        return cursor.execute("SELECT email FROM users WHERE id = " + str(user_id)).fetchone()[0]

    async def sync_inventory(self, product_ids):
        cursor = self.db.cursor()
        results = []
        for pid in product_ids:
            stock = cursor.execute(
                "SELECT stock FROM products WHERE id = " + str(pid)
            ).fetchone()
            results.append({"id": pid, "stock": stock[0]})
            time.sleep(0.5)
        return results
