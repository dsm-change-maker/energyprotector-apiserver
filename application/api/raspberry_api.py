import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))
from flask_jwt_extended import(
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)
from application.models import Device, Raspberry, Unit, UsingTime
from application import db, jwt
from flask import Blueprint, request
import datetime


access_token_exdelta = datetime.timedelta(hours=10)
refresh_token_exdelta = datetime.timedelta(weeks=2)

bp = Blueprint('raspberry', __name__)


@bp.route('/api/raspberry/connect', methods=['POST'])
def connect_raspberry():
    data = request.json

    raspberry = Raspberry.query.filter_by(id=data['raspberry_id']).first()
    if raspberry is None or raspberry.pw != data['raspberry_pw'] or raspberry.group != data['raspberry_group']:
        return {"message":"아이디 혹은 패스워드가 일치하지 않습니다.", 'data':{}}, 400
  

    return {'access_token':  create_access_token(raspberry.key, expires_delta=access_token_exdelta),'refresh_token': create_refresh_token(raspberry.key, expires_delta=refresh_token_exdelta)}, 200


@bp.route('/api/raspberry', methods=['GET'])
@jwt_required
def view_raspberry():
    raspberry = Raspberry.query.get(get_jwt_identity())
    devices = Device.query.filter_by(rasp_key=get_jwt_identity()).all()
    
    return {'raspberry_group':raspberry.group,'raspberry_id':raspberry.id, 'remote_control':raspberry.remote_control, 'raspberry_devices':[d.to_dict() for d in devices]}, 200


@bp.route('/api/raspberry', methods=['POST'])
def post_raspberry():
    data = request.json
    rasp = Raspberry(group=data['raspberry_group'], id=data['raspberry_id'], pw=data['raspberry_pw'], remote_control=data['remote_control'])
    db.session.add(rasp)
    db.session.commit()
    using = UsingTime(rasp_key=rasp.key, time=0, date=str(datetime.date.today()))
    db.session.add(using)
    db.session.commit()

    return {"message":"라즈베리파이 정보가 등록되었습니다"}, 201


@bp.route('/api/raspberry', methods=['PUT'])
@jwt_required
def modify_raspberry():
    data = request.json
    rasp = Raspberry.query.filter_by(id=get_jwt_identity(), group=data['raspberry_group']).first()
    if rasp is None:
        return {"message" : "수정할 디바이스 정보가 없습니다."}, 404

    rasp.pw = data['raspberry_pw']
    rasp.remote_control = data['remote_control']
    rasp.group = data['raspberry_group']
    
    return {"message" : "디바이스 정보가 수정되었습니다."}, 200


@bp.route('/api/raspberry', methods=['DELETE'])
@jwt_required
def delete_raspberry():
    rasp = Raspberry.query.get(get_jwt_identity())
    using_time = UsingTime.query.filter_by(rasp_key=get_jwt_identity()).first()
    db.session.delete(using_time)

    if rasp is None:
        return {"message" : "삭제할 라즈베리파이 정보가 없습니다."}, 404
    
    for device in Device.query.filter_by(rasp_key=get_jwt_identity()).all():
        for unit in Unit.query.filter_by(device_key=device.key).all():
            db.session.delete(unit)
        db.session.delete(device)
    
    db.session.delete(rasp)
    db.session.commit()

    return {"message":"디바이스가 성공적으로 삭제 되었습니다."}, 200

@bp.route('/api/reset')
def reset():
    for rasp in Raspberry.query.all():
        using = UsingTime(rasp_key=rasp.key, time=0, date=datetime.date.today())
        db.session.add(using)

    db.session.commit()
    return {"message":"reset"}

