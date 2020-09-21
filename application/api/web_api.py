import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))
from application.models import Device, Raspberry, Unit, UsingTime
from application import db, jwt
from flask import Blueprint, request, jsonify
import datetime
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

bp = Blueprint('web', __name__)
access_token_exdelta = datetime.timedelta(hours=10)
refresh_token_exdelta = datetime.timedelta(weeks=2)

@bp.route('/api/web/login', methods=['POST'])
def login():
    data = request.json
    raspberry = Raspberry.query.filter_by(group=data['raspberry_group'], id=data['raspberry_id'], pw=data['raspberry_pw']).first()
    if raspberry is None:
        return {"message":"아이디 혹은 패스워드가 일치하지 않습니다."}, 400

    return {'access_token': create_access_token(raspberry.key, expires_delta=access_token_exdelta),'refresh_token': create_refresh_token(raspberry.key, expires_delta=refresh_token_exdelta)}, 200



@bp.route('/api/web/devices', methods=['GET'])
@jwt_required
def view_devices():
    devices = Device.query.filter_by(rasp_key=get_jwt_identity()).all()
    return {"devices":[d.to_dict() for d in devices]}, 200


@bp.route('/api/web/units/<string:device_id>', methods=['GET'])
@jwt_required
def view_units(device_id):
    data = request.json
    device = Device.query.filter_by(rasp_key=get_jwt_identity(), id=device_id).first()
    units = Unit.query.filter_by(device_key=device.key).all()
    return {"units":[u.to_dict() for u in units]}, 200

