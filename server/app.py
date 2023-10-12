#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''
class ScientistList(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientist_dict = [scientist.to_dict(rules = ('-missions',)) for scientist in scientists]
        return make_response(scientist_dict, 200)
    def post(self):
        data = request.json
        try:    
            new_scientist = Scientist(
            name = data['name'], 
            field_of_study = data['field_of_study']
            )
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(rules = ('-missions',)), 201)
        except ValueError: 
            return make_response({"errors": ["validation errors"]}, 400)
api.add_resource(ScientistList, "/scientists")


class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist: 
            return make_response({"error": "Scientist not found"}, 404)
        scientist_to_dict = scientist.to_dict()
        return make_response(scientist_to_dict, 200)
    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if scientist is None:
           return make_response({"error" : "Scientist not found" }, 404)
        try:
            setattr(scientist, "name", request.json['name'])
            setattr(scientist, "field_of_study", request.json['field_of_study'])
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(rules = ('-missions',)), 202)
        except ValueError: 
            return make_response({"errors": ["validation errors"]}, 400)
    def delete(self, id):
        scientist = Scientist.query.filter_by(id = id).first()
        if scientist is None:
            return make_response({"error" : "Scientist not found"}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({},204)
    
api.add_resource(ScientistById, '/scientists/<int:id>')

class PlanetList(Resource):
    def get(self):
        planets = Planet.query.all()
        planet_dict = [planet.to_dict(rules = ('-missions',)) for planet in planets]
        return make_response(planet_dict, 200)

api.add_resource(PlanetList, '/planets')

class MissionList(Resource):
     def post(self):
        data = request.get_json()
        try:    
            new_mission = Mission(
            name = data['name'], 
            scientist_id = data['scientist_id'],
            planet_id = data['planet_id'],
            )
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError: 
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(MissionList, '/missions')
         


if __name__ == '__main__':
    app.run(port=5555, debug=True)
