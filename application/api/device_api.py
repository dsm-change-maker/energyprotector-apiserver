from application.models import Device, Raspberry
from application import db
from flask import Blueprint, request

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))


bp = Blueprint('device', __name__)


@bp.route('/api/device/<string:device_id>', methods=['GET'])
def show_device(device_id):
    device = Device.query.filter_by(device_id=device_id).first()
    rasp = Raspberry.query.get(device.pi_key)
    if rasp is None:
        return {'is_success': True, 'device_id': id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': '', 'connected_raspberry_id': '', 'on_off': device.onoff}

    return {'is_success': True, 'device_id': id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': rasp.rasp_group, 'connected_raspberry_id': rasp.rasp_id, 'on_off': device.onoff}


@bp.route('/api/device/', methods=['POST'])
def post_device():
    data = request.json
    device = Device(device_id=data['device_id'], device_type=data['device_type'],
                    moter_count=data['moter_count'], pi_key=1)

    db.session.add(device)
    db.session.commit()
    return {'is_succcess': True}


@bp.route('/api/device/<string:device_id>', methods=['PUT'])
def modify_device(device_id):
    data = request.json
    device = Device.query.filter_by(device_id=device_id).first()
    device.device_id = data['device_id']
    device.device_type = data['device_type']
    device.moter_count = data['moter_count']

    db.session.commit()
    return {'is_succcess': True}
