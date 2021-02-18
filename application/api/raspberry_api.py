import datetime
from flask import Blueprint, request
from application import db, jwt
from application.models import Device, Raspberry, Unit, UsingTimeDay, UsingTimeMonth, UsingTimeYear
from flask_jwt_extended import(
    jwt_required,
    create_access_token,
    get_jwt_identity
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))


access_token_exdelta = datetime.timedelta(days=30)

bp = Blueprint('raspberry', __name__)


@bp.route('/api/raspberry/connect', methods=['POST'])
def connect_raspberry():
    json = request.json

    raspberry = Raspberry.query.filter_by(id=json['raspberry_id']).first()
    if raspberry is None or raspberry.pw != json['raspberry_pw'] or raspberry.group != json['raspberry_group']:
        return {"message": "아이디 혹은 패스워드가 일치하지 않습니다."}, 400

    return {'access_token':  create_access_token(raspberry.key, expires_delta=access_token_exdelta)}, 200


@bp.route('/api/raspberry', methods=['GET'])
@jwt_required
def view_raspberry():
    raspberry = Raspberry.query.get(get_jwt_identity())
    devices = raspberry.devices.split(',')
    devices_array = []
    for device in devices:
        device_info = device.split(';')
        device_ip = Device.query.filter_by(id=device_info[0], type=device_info[1]).first().ip
        try:
            devices_array.append(
                {"device_id": device_info[0], "device_ip": device_info[1]})
        except:
            pass

    return {'remote_control': raspberry.remote_control, 'raspberry_devices': devices_array}, 200


@bp.route('/api/raspberry', methods=['POST'])
def post_raspberry():
    json = request.json
    if Raspberry.query.filter_by(group=json['raspberry_group'], id=json['raspberry_id']).first() is not None:
        return {"message": "같은 이름의 라즈베리파이가 존재합니다."}, 400

    devices = ''
    for device_info in json['devices']:
        devices += device_info['device_id'] + ';'
        devices += device_info['device_type'] + ','

    print("check")
    rasp = Raspberry(group=json['raspberry_group'], id=json['raspberry_id'],
                     pw=json['raspberry_pw'], remote_control=json['remote_control'], devices=devices, start_date=str(datetime.date.today()))
    db.session.add(rasp)
    db.session.commit()

    return {"message": "라즈베리파이 정보가 등록되었습니다"}, 201


@bp.route('/api/raspberry', methods=['PUT'])
@jwt_required
def modify_raspberry():
    json = request.json
    rasp = Raspberry.query.filter_by(
        key=get_jwt_identity(), id=json['raspberry_id'], group=json['raspberry_group']).first()
    if rasp is None:
        return {"message": "수정할 디바이스 정보가 없습니다."}, 404

    rasp.pw = json['raspberry_pw']
    rasp.remote_control = json['remote_control']

    return {"message": "디바이스 정보가 수정되었습니다."}, 200


@bp.route('/api/raspberry', methods=['DELETE'])
@jwt_required
def delete_raspberry():
    rasp = Raspberry.query.get(get_jwt_identity())
    if rasp is None:
        return {"message": "삭제할 라즈베리파이 정보가 없습니다."}, 404

    using_time_days = UsingTimeDay.query.filter_by(key=get_jwt_identity()).all()
    using_time_months = UsingTimeMonth.query.filter_by(key=get_jwt_identity()).all()
    using_time_years = UsingTimeYear.query.filter_by(key=get_jwt_identity()).all()   
    for using_time_day in using_time_days:
        db.session.delete(using_time_day)
    for using_time_month in using_time_months:
        db.session.delete(using_time_month)
    for using_time_year in using_time_years:
        db.session.delete(using_time_year)

    devices_info = rasp.devices.split(',')
    for device_info in devices_info[:-1]:
        device = Device.query.filter_by(
            id=device_info[0], type=device_info[1]).first()
        try:
            for unit in Unit.query.filter_by(device_key=device.key).all():
                db.session.delete(unit)
            db.session.delete(device)
        except:
            pass

    db.session.delete(rasp)
    db.session.commit()

    return {"message": "디바이스가 성공적으로 삭제 되었습니다."}, 200
