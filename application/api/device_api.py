from flask import Blueprint, request
import datetime
from ep_sock.client import ClientSendSignal
from ep_sock.socket_client_api import RunClientApiThread
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
from application import db, jwt
from application.models import Device, Raspberry, Unit, UsingTimeDay, UsingTimeMonth, UsingTimeYear
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))

bp = Blueprint('device', __name__)
SERVER_URL = '13.125.133.6'
SERVER_PORT = 56548

@bp.route('/api/device', methods=['GET'])
@jwt_required
def view_device():
    parameters = request.args
    device = Device.query.filter_by(
        id=parameters['device_id'], type=parameters['device_type']).first()
    if device is None:
        return {'message': "해당 디바이스 정보를 찾을 수 없습니다."}, 404
    units = Unit.query.filter_by(device_key=device.key).all()

    return {"device_ip": device.ip, "unit_count": device.unit_count, "units": [u.to_dict() for u in units]}, 200


@bp.route('/api/device', methods=['POST'])
def post_device():
    json = request.json
    if Device.query.filter_by(id=json['device_id'], type=json['device_type']).first() is not None:
        return {"message": "이미 같은 이름의 디바이스가 존재합니다."}, 400

    device = Device(id=json['device_id'], type=json['device_type'],
                    unit_count=json['unit_count'], ip=json['device_ip'])
    db.session.add(device)
    db.session.commit()
    for i in range(0, json['unit_count']):
        unit = Unit(index=i, device_key=device.key)
        db.session.add(unit)
    db.session.commit()
    return {'message': '디바이스 정보가 등록되었습니다.'}, 200


@bp.route('/api/device', methods=['PUT'])
def modify_device():
    json = request.json
    device = Device.query.filter_by(
        id=json['device_id'], type=json['device_type']).first()
    if device is None:
        return {'message': '수정할 디바이스 정보를 찾을 수 없습니다'}, 404

    device.ip = json['device_ip']

    db.session.commit()
    return {'message': '디바이스 정보가 수정되었습니다.'}, 200


@bp.route('/api/device', methods=['DELETE'])
@jwt_required
def delete_device():
    json = request.json
    raspberry = Raspberry.query.get(get_jwt_identity())
    devices = raspberry.devices.split(',')
    for device in devices:
        device_info = device.split(';')
        if device_info[0] == json['device_id'] and device_info[1] == json['device_type']:
            devices.remove(device)
            raspberry.devices = ','.join(devices)
            device = Device.query.filter_by(
                id=json['device_id'], type=json['device_type']).first()
            for unit in Unit.query.filter_by(device_key=device.key).all():
                db.session.delete(unit)
                db.session.delete(device)
            db.session.commit()    
            return {'message': '디바이스 정보가 삭제되었습니다.'}, 200
    return {"message": "삭제할 디바이스 정보가 없습니다,"}, 404


@bp.route('/api/device/control', methods=['POST'])
@jwt_required
def control_device():
    json = request.json
    raspberry = Raspberry.query.get(get_jwt_identity())
    devices = raspberry.devices.split(',')

    for device in devices[:-1]:
        device_info = device.split(';')
        if device_info[0] == json['device_id'] and device_info[1] == json['device_type']:
            device = Device.query.filter_by(
                id=json['device_id'], type=json['device_type']).first()
            unit = Unit.query.filter_by(
                device_key=device.key, index=json['unit_index']).first()
            if unit is None:
                return {"message": "컨트롤할 디바이스 정보를 찾을 수 없습니다."}, 404
            if not Raspberry.query.get(get_jwt_identity()).remote_control:
                return {"message": "접근 권한이 없습니다."}, 401

#-----------------------------Socket----------------------------# 
            send_signal = ClientSendSignal()
            run_client_api_thread = RunClientApiThread(send_signal, host=SERVER_URL, port=SERVER_PORT,
                                                    debug=True)
            run_client_api_thread.start()
            
            send_signal.raspberry_id = str(raspberry.id)
            send_signal.raspberry_group = str(raspberry.group)
            send_signal.device_id = str(json['device_id'])
            send_signal.device_type = str(json['device_type'])
            send_signal.unit_index = json['unit_index']
            send_signal.on_off = json['on_off']
            send_signal.send = True
            while True:
                if not send_signal.send:
                    break
            print('REQ OK : ', send_signal.req_ok)
            send_signal.close = True
            while True:
                if not send_signal.close:
                    break
#----------------------------------------------------------------#
            if json['on_off']:
                unit.on_off = True
                unit.start = datetime.datetime.now()
                db.session.commit()
                return {'message': '디바이스를 성공적으로 제어했습니다.'}, 200
            else:
                today = datetime.date.today()
                key = get_jwt_identity()
                unit.on_off = False
                time = datetime.datetime.now() - unit.start
                using_day = UsingTimeDay.query.filter_by(
                    date=today.strftime('%Y-%m-%d'), rasp_key=get_jwt_identity()).first()
                if using_day is None:
                    using_day = UsingTimeDay(rasp_key=get_jwt_identity(), time=0,
                                             date=today.strftime('%Y-%m-%d'))
                    db.session.add(using_day)
                using_month = UsingTimeMonth.query.filter_by(
                    date=today.strftime('%Y-%m'), key=key).first()
                if using_month is None:
                    using_month = UsingTimeMonth(rasp_key=get_jwt_identity(), time=0,
                                                 date=today.strftime('%Y-%m'))
                    db.session.add(using_month)
                using_year = UsingTimeYear.query.filter_by(
                    date=today.strftime('%Y'), rasp_key=get_jwt_identity()).first()
                if using_year is None:
                    using_year = UsingTimeYear(rasp_key=get_jwt_identity(), time=0,
                                               date=today.strftime('%Y'))
                    db.session.add(using_year)
                using_day.time += time.seconds
                using_month.time += time.seconds
                using_year.time += time.seconds



                db.session.commit()
                return {'message': '디바이스를 성공적으로 제어했습니다.'}, 200
