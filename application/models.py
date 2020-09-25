from application import db
import os
import sys
sys.path.append(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__))))


class Device(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(64))
    type = db.Column(db.String(64), nullable=False)
    unit_count = db.Column(db.Integer)
    ip = db.Column(db.String(32))

    def to_dict(self):
        return {
            "device_id": self.id,
            "device_type":self.type,
            "unit_count":self.unit_count,
            "device_ip" : self.ip
        }


class Raspberry(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(64), nullable=False)
    id = db.Column(db.String(64), nullable=False)
    pw = db.Column(db.String(64), nullable=False)
    remote_control = db.Column(db.Boolean, default=True)
    devices = db.Column(db.Text)


class Unit(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer, nullable=False)
    device_key = db.Column(db.Integer, db.ForeignKey('device.key'))
    on_off = db.Column(db.Boolean, default=False)
    start = db.Column(db.DateTime())

    def to_dict(self):
        return {
            "index": self.index,
            "on_off": self.on_off
        }


class UsingTime(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String)
    time = db.Column(db.Integer)
