#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
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

class Restaurants(Resource):
    def get(self):
        restaurants = [restaurant.to_dict() for restaurant in Restaurant.query.all()]
        return make_response(jsonify(restaurants), 200)
    
api.add_resource(Restaurants, '/restaurants')

class RestaurantByID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if restaurant:
            return make_response(jsonify(restaurant.to_dict()), 200)
        return make_response(jsonify({"message": "Restaurant not found"}), 404)
    
    def delete(self,id):
        record = Restaurant.query.filter(Restaurant.id == id).first()
        db.session.delete(record)
        db.session.commit()
        
        return make_response(
            jsonify({"message": "Restaurant deleted successfully"}), 204
        )
api.add_resource(RestaurantByID, '/restaurants/<int:id>')

class Pizzas(Resource):
    def get(self):
        pizzas = [pizza.to_dict() for pizza in Pizza.query.all()]
        return make_response(jsonify(pizzas), 200)
    
api.add_resource(Pizzas, '/pizzas')

class RestaurantPizzas(Resource):
    def get(self):
        restaurant_pizzas = [restaurant_pizza.to_dict() for restaurant_pizza in RestaurantPizza.query.all()]
        return make_response(jsonify(restaurant_pizzas), 200)
    
    def post(self):
        data = request.get_json()
        restaurant_id = data.get("restaurant_id")
        pizza_id = data.get("pizza_id")
        price = data.get("price")
        
        if not restaurant_id or not pizza_id or not price:
            return make_response(
                jsonify({"message": "Missing required fields"}), 400
            )
        
        restaurant = Restaurant.query.filter_by(id=restaurant_id).first()
        pizza = Pizza.query.filter_by(id=pizza_id).first()
        
        if not restaurant or not pizza:
            return make_response(
                jsonify({"message": "Restaurant or Pizza not found"}), 404
            )
        
        restaurant_pizza = RestaurantPizza(restaurant=restaurant, pizza=pizza, price=price)
        db.session.add(restaurant_pizza)
        db.session.commit()
        
        return make_response(jsonify(restaurant_pizza.to_dict()), 201)
    
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)