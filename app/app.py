
from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            food_item VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "UP"
    })


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    customer_name = data.get("customer_name")
    food_item = data.get("food_item")
    quantity = data.get("quantity")

    if not customer_name or not food_item or not quantity:
        return jsonify({
            "error": "customer_name, food_item and quantity are required"
        }), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO orders (customer_name, food_item, quantity)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (customer_name, food_item, quantity)
    )

    order_id = cursor.fetchone()[0]

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({
        "message": "Order created successfully",
        "order_id": order_id
    }), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer_name, food_item, quantity
        FROM orders
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    orders = []

    for row in rows:
        orders.append({
            "id": row[0],
            "customer_name": row[1],
            "food_item": row[2],
            "quantity": row[3]
        })

    return jsonify(orders)


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5000
    )
