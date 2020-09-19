import os
import sys
sys.path.append(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__))))
    
from application import db

class Device(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64), unique=True)
    type = db.Column(db.String(64), nullable=False)
    unit_count = db.Column(db.Integer)
    ip = db.Column(db.String(32))
    rasp_key = db.Column(db.Integer, db.ForeignKey('raspberry.key'))


class Raspberry(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(64), nullable=False)
    id = db.Column(db.String(64), nullable=False)
    pw = db.Column(db.String(64), nullable=False)
    remote_control = db.Column(db.Boolean, default=True)


class Unit(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    device_id = db.Column(db.String(64), db.ForeignKey('device.id'))
    on_off = db.Column(db.Boolean, default=False)
    start = db.Column(db.DateTime())

class UsingTime(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    rasp_key = db.Column(db.Integer, db.ForeignKey('raspberry.key'))
    date = db.Column(db.DateTime())
    time = db.Column(db.Integer)
