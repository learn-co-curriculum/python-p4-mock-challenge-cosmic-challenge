#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Planet, Scientist, Mission

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return ''

@app.route('/scientists', methods=['GET', 'POST'])
def scientists():
    if request.method == 'GET':
        return [scientists.todict(rules=('-missions','-planets')) for scientist in Scientist.query.all()]
    elif request.method == 'POST':
        fields = request.get_json()
        try:
            scientist = Scientist(
                name=fields['name'],
                field_of_study=fields['field_of_study'],
                avatar=fields['avatar']
            )
            db.session.add(scientist)
            db.session.commit()
            return scientist.to_dict()
        except ValueError:
            return {'error': '400: Validation error'}, 400
        
@app.route('/scientists/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def scientist_by_id(id):
    scientist = Scientist.query.filter(Scientist.id == id).one_or_none()
    if scientist:
        if request.method == 'GET':
            return scientist.to_dict()
        elif request.method == 'PATCH':
            fields = request.get_json()
            try:
                for field in fields:
                    setattr(scientist, field, fields[field])
                db.session.add(scientist)
                db.session.commit()
                return scientist.to_dict(rules=('-missions', 'planets')), 202
            except ValueError:
                return {'error': '400: Validation Error'}, 400 
        elif request.method == 'DELETE':
            db.session.delete(scientist)
            db.session.commit()
            return {}, 204
    return {'error': '404: Scientist not found'}

@app.route('/planets', methods=['GET'])
def planets():
    if request.method == 'GET':
        return [planet.to_dict(rules=('-missions', '-scientists')) for planet in Planet.query.all()]
    
@app.route('/missions', methods=['POST'])
def create_mission():
    if request.method == 'POST':
        fields = request.getjson()
        try:
            mission = Mission(
                name=fields['name'],
                scientist_id=fields['scientist_id'],
                planet_id=fields['planet_id']
            )
            db.session.add(mission)
            db.session.commit()
            return mission.to_dict()
        except ValueError:
            return {'error': '400: Validation error'}, 400

if __name__ == '__main__':
    app.run(port=5555, debug=True)