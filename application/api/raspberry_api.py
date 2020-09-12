import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))
    
from application.models import Device, Raspberry
from application import db
from flask import Blueprint, request
import datetime



bp = Blueprint('raspberry', __name__)

@bp.route('/api/device/<string:device_id>', methods=['GET'])
def show_device(device_id):
    device = Device.query.filter_by(device_id=device_id).first()
    rasp = Raspberry.query.get(device.pi_key)
    if rasp is None:
        return {'is_success': True, 'device_id': device_id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': '', 'connected_raspberry_id': '', 'on_off': device.onoff}
    else:
        return {'is_success': True, 'device_id': device_id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': rasp.rasp_group, 'connected_raspberry_id': rasp.rasp_id, 'on_off': device.onoff}

