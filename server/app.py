#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
class Restaurants(Resource):
    def get(self):
        restaurant_list = [restaurant.to_dict(
            rules=("-restaurant_pizzas",)
        ) for restaurant in Restaurant.query.all()]
        return make_response(restaurant_list, 200)

# GET and DELETE /restaurants/int:id
class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)
        
        return make_response(restaurant.to_dict(), 200)
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).one_or_none()
        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)

# GET /pizzas
class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict(only=("id", "ingredients", "name"))
                  for pizza in Pizza.query.all()]
        return make_response(pizzas, 200)

# POST /pizzas
class RestaurantPizzas(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_restaurant_pizza = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )

            db.session.add(new_restaurant_pizza)
            db.session.commit()
            return make_response(new_restaurant_pizza.to_dict(), 201)
        
        except (KeyError, ValueError):
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)
        
api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
