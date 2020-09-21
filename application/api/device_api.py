import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))
from application.models import Device, Raspberry, Unit, UsingTime
from application import db, jwt
from flask_jwt_extended import (
    get_jwt_identity,
    jwt_required,
)
import datetime
from flask import Blueprint, request

bp = Blueprint('device', __name__)


@bp.route('/api/device/<string:device_id>', methods=['GET'])
@jwt_required
def view_device(device_id):
    device = Device.query.filter_by(id=device_id, rasp_key=get_jwt_identity()).first()
    if device is None:
        return {'message': "디바이스 정보가 없습니다."}, 404
    units = Unit.query.filter_by(device_key=device.key).all()

    return {"device_type":device.type, "device_ip":device.ip, "unit_count":device.unit_count, "units" : [u.to_dict() for u in units]}, 200


@bp.route('/api/device', methods=['POST'])
@jwt_required
def post_device():
    data = request.json
    device = Device(id=data['device_id'], type=data['device_type'],
                    unit_count=data['unit_count'], ip=data['device_ip'], rasp_key=get_jwt_identity())
    db.session.add(device)
    db.session.commit()                
    for i in range (0, data['unit_count']):
        unit = Unit(index=i, device_key=device.key)
        db.session.add(unit)
    db.session.commit()
    return {'message': '디바이스 정보가 등록되었습니다.', 'data': {}}, 200


@bp.route('/api/device', methods=['PUT'])
@jwt_required
def modify_device():
    data = request.json 
    device = Device.query.filter_by(device_id=data['device_id'], rasp_key=get_jwt_identity()).first()
    if device is None:
        return {'message': '수정할 디바이스 정보를 찾을 수 없습니다', 'data': {}}, 404

    device.device_type = data['device_type']
    device.device_ip = data['device_ip']

    db.session.commit()
    return {'message': '디바이스 정보가 수정되었습니다.', 'data': {}}, 200


@bp.route('/api/device', methods=['DELETE'])
@jwt_required
def delete_device():
    device_id = request.json['device_id']
    device = Device.query.filter_by(id=device_id, rasp_key=get_jwt_identity()).first()
    if device is None:
        return {'message': '삭제할 디바이스 정보를 찾을 수 없습니다.', 'data': {}}, 404
    for unit in Unit.query.filter_by(device_key=device.key):
        db.session.delete(unit)

    db.session.delete(device)
    db.session.commit()
    return {'message': '디바이스 정보가 삭제되었습니다.', 'data': {}}, 200


@bp.route('/api/device/control/<unit_index>', methods=['POST'])
@jwt_required
def control_device(unit_index):
    data = request.json
    device = Device.query.filter_by(id=data['device_id'], rasp_key=get_jwt_identity()).first()
    if device is None:
        return {"message":"컨트롤할 디바이스 정보를 찾을 수 없습니다."}, 404

    unit = Unit.query.filter_by(device_key=device.key, index=unit_index).first()
    if unit is None:
        return {"message":"컨트롤할 디바이스 정보를 찾을 수 없습니다."}, 404
    
      
    if not Raspberry.query.get(get_jwt_identity()).remote_control:
        return {"message":"디바이스를 컨트롤 할 수 없습니다."}, 401


    if data['on_off']:
        unit.on_off = True
        unit.start = datetime.datetime.now()
        db.session.commit()
        return {'message' : '디바이스를 성공적으로 제어했습니다.', 'data' : {}}, 200
    else:
        unit.on_off = False
        time = datetime.datetime.now() - unit.start
        using = UsingTime.query.filter_by(date=str(datetime.date.today()), rasp_key=str(get_jwt_identity())).first()
        using.time += time.seconds
        db.session.commit()
        return {'message': '디바이스를 성공적으로 제어했습니다.', 'data':{}}, 200



