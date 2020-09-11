from application import db
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class Device(db.Model):
    device_id = db.Column(db.String(64), primary_key=True)
    device_type = db.Column(db.String(64), nullable=False)
    onoff = db.Column(db.Boolean(), default=False)
    start = db.Column(db.DateTime())
    end = db.Column(db.DateTime())
    moter_count = db.Column(db.Integer)
    pi_key = db.Column(db.Integer, db.ForeignKey(
        'raspberry.key', ondelete="CASCADE"),)


class Raspberry(db.Model):
    key = db.Column(db.Integer, primary_key=True)
    rasp_group = db.Column(db.String(64), nullable=False)
    rasp_id = db.Column(db.String(64), nullable=False)
    rasp_pw = db.Column(db.String(64), nullable=False)


# class Usingtime(db.Model):
#     __tablename__ = 'usingtime'
