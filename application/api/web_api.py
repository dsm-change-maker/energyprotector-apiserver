from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, request, jsonify
from application import db, jwt
from application.models import Device, Raspberry, Unit, UsingTime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))

bp = Blueprint('web', __name__)
access_token_exdelta = datetime.timedelta(hours=10)
refresh_token_exdelta = datetime.timedelta(weeks=2)


@bp.route('/api/web/login', methods=['POST'])
def login():
    data = request.json
    raspberry = Raspberry.query.filter_by(
        group=data['raspberry_group'], id=data['raspberry_id'], pw=data['raspberry_pw']).first()
    if raspberry is None:
        return {"message": "아이디 혹은 패스워드가 일치하지 않습니다."}, 400

    return {'access_token': create_access_token(raspberry.key, expires_delta=access_token_exdelta)}, 200


@bp.route('/api/web/devices', methods=['GET'])
@jwt_required
def view_devices():
    rasp = Raspberry.query.get(get_jwt_identity())
    devices = rasp.devices.split(',')
    devices_info = []
    for device in devices[:-1]:
        device_info = device.split(';')
        device = Device.query.filter_by(
            id=device_info[0], type=device_info[1]).first()
        devices_info.append({"device_id": device.id, "device_type": device.type, "unit_count": device.unit_count})
    return {"devices": devices_info}, 200


@bp.route('/api/web/units', methods=['GET'])
@jwt_required
def view_units(device_id):
    parameters = request.args
    rasp = Raspberry.query.get(get_jwt_identity())
    devices = rasp.devices.split(',')
    for device in devices[:-1]:
        device_info = devices.split(';')
        if device_info[0] == parameters['device_id'] and device_info[1] == parameters['device_type']:
            units = Unit.query.filter_by(
                device_key=parameters['device_id']).all()
            return {"units": [u.to_dict() for u in units]}, 200
    return {"message": "잘못된 요청입니다."}, 400

# @bp.route('/api/web/using-time', methods=['GET'])
# def using_time():
#     parameters = request.args
#     rasp = Raspberry.query.filter_by(group=parameters['raspberry_group'], id=parameters['raspberry_id']).first()
#     using_time = UsingTime.query.get(rasp.key)
#     if parameters['year']:
#         today_date = datetime.date.today()
#         start_date = today_date - relativedelta(years=parameters['year_n'])

#     elif parameters['month']:
#         today_date = datetime.date.today()
        
#     else: