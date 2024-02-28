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
    return 'PRACTICE CODE CHALLENGE'  


class Scientists(Resource):

    def get(self):
        scientists = [scientist.to_dict(rules=('-missions', '-planets',))
                      for scientist in Scientist.query.all()]

        return make_response(scientists, 200)

    def post(self):

        fields = request.get_json()
        try:
            scientist = Scientist(
                name=fields['name'],
                field_of_study=fields['field_of_study']
            )
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(rules=('-missions',)), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Scientists, "/scientists")


class ScientistById(Resource):

    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()

        if scientist is None:
            return make_response({'error': 'Scientist not found'}, 404)

        return make_response(scientist.to_dict(), 200)

    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()

        if scientist is None:
            return make_response({'error': 'Scientist not found'}, 404)

        fields = request.get_json()

        try:
            for field in fields:
                setattr(scientist, field, fields[field])
            db.session.add(scientist)
            db.session.commit()

            return make_response(scientist.to_dict(rules=('-planets', '-missions')), 202)

        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).one_or_none()

        if scientist is None:
            return make_response({'error': 'Scientist not found'}, 404)

        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)


api.add_resource(ScientistById, "/scientists/<int:id>")


class Planets(Resource):

    def get(self):
        planets = [planet.to_dict(rules=('-missions', '-scientists',))
                   for planet in Planet.query.all()]

        return make_response(planets, 200)


api.add_resource(Planets, "/planets")


class Missions(Resource):
    def post(self):

        fields = request.get_json()
        try:
            mission = Mission(
                name=fields['name'],
                scientist_id=fields['scientist_id'],
                planet_id=fields['planet_id'])
            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Missions, "/missions")

if __name__ == '__main__':
    app.run(port=5555, debug=True)

