import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(os.path.dirname(__file__)))))

from application.models import Device, Raspberry
from application import db
from flask import Blueprint, request
import datetime



bp = Blueprint('raspberry', __name__)

@bp.route('/api/raspberry/connect', methods=['POST'])
def show_device():
    data = request.json
    rasp_id = data['raspberry_id']
    rasp_pw = data['raspberry_pw']

    raspberry = Device.query.filter_by(rasp_id=rasp_id).first()
    if raspberry is None and raspberry.rasp_pw != rasp_pw:
        return {'is_success': False, "msg":"아이디 혹은 패스워드가 일치하지 않습니다."}
    rasp = Raspberry.query.get(device.pi_key)
    if rasp is None:
        return {'is_success': True, 'device_id': device_id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': '', 'connected_raspberry_id': '', 'on_off': device.onoff}
    else:
        return {'is_success': True, 'device_id': device_id, 'device_type': device.device_type, 'moter_count': device.moter_count, 'connected_raspberry_group': rasp.rasp_group, 'connected_raspberry_id': rasp.rasp_id, 'on_off': device.onoff}

