from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
  "ix": "ix_%(column_0_label)s",
  "uq": "uq_%(table_name)s_%(column_0_name)s",
  "ck": "ck_%(table_name)s_%(constraint_name)s",
  "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
  "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)

class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    serialize_rules = ('-missions.planet', '-scientists.planets')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)

    missions = db.relationship('Mission', backref='planet')
    scientists = association_proxy('missions', 'scientist',
        creator=lambda sci: Mission(scientist=sci))

class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    serialize_rules = ('-missions.scientist', '-planets.scientists')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    field_of_study = db.Column(db.String)
    avatar = db.Column(db.String)

    missions = db.relationship('Mission', backref='scientist')
    planets = association_proxy('missions', 'planet',
        creator=lambda plt: Mission(planet=plt))
    
    @validates('name')
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError('Scientist must have name.')
    
    @validates('field_of_study')
    def validate_name(self, key, field_of_study):
        if field_of_study:
            return field_of_study
        raise ValueError('Scientist must have field of study.')

class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    serialize_rules = ('-scientist.missions', '-planet.missions')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    @validates('name')
    def validate_name(self, key, name):
        if name:
            return name
        raise ValueError('Mission must have name.')
    
    @validates('scientist_id')
    def validate_name(self, key, scientist_id):
        if scientist_id:
            return scientist_id
        raise ValueError('Mission must have scientist ID.')
    
    @validates('planet_id')
    def validate_name(self, key, planet_id):
        if planet_id:
            return planet_id
        raise ValueError('Mission must have planet ID.')

# add any models you may need. 