#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([r.to_dict(["id", "name", "address"]) for r in restaurants]), 200


@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def restaurant_detail(id):
    restaurant = Restaurant.query.get(id)
    if request.method == "GET":
        if restaurant:
            return jsonify(restaurant.to_dict(["id", "name", "address", "restaurant_pizzas"])), 200
        return jsonify({"error": "Restaurant not found"}), 404
    elif request.method == "DELETE":
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([p.to_dict(["id", "name", "ingredients"]) for p in pizzas]), 200


@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        price = data["price"]
        pizza_id = data["pizza_id"]
        restaurant_id = data["restaurant_id"]
        restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
        db.session.add(restaurant_pizza)
        db.session.commit()
        return jsonify(restaurant_pizza.to_dict({
            "id": None,
            "price": None,
            "pizza_id": None,
            "restaurant_id": None,
            "pizza": ["id", "name", "ingredients"],
            "restaurant": ["id", "name", "address"]
        })), 201
    except Exception as e:
        import sys
        print(f"Error in create_restaurant_pizza: {e}", file=sys.stderr)
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400


if __name__ == "__main__":
    app.run(port=5555, debug=True)
