from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
import datetime
from dateutil.relativedelta import relativedelta
from flask import Blueprint, request
from application.models import Device, Raspberry, Unit, UsingTimeDay, UsingTimeMonth, UsingTimeYear
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
        units_info = []
        for unit in Unit.query.filter_by(device_key=device.key).all():
            units_info.append(unit.on_off)
        devices_info.append(
            {"device_id": device.id, "device_type": device.type, "unit_count": device.unit_count, "unit_info": units_info})
    return {"devices": devices_info}, 200


@bp.route('/api/web/using-time', methods=['GET'])
def using_time():
    parameters = request.args
    rasp = Raspberry.query.filter_by(
        group=parameters['raspberry_group'], id=parameters['raspberry_id']).first()
    this_date = datetime.date.today()
    rasp_date = datetime.datetime.strptime(rasp.start_date, "%Y-%m-%d").date()
    if int(parameters['year']) == 1:
        year = []
        start_date = this_date - relativedelta(years=int(parameters['year_n']))
        if start_date < rasp_date:
            start_date = rasp_date
            while start_date <= this_date:
                year.append([start_date.strftime('%Y'), UsingTimeYear.query.filter_by(key=rasp.key, date=start_date.strftime('%Y')).first().time])
                start_date= start_date + relativedelta(years=1)
        else:
            while start_date <= this_date:
                year.append([start_date.strftime('%Y'), UsingTimeYear.query.filter_by(key=rasp.key, date=start_date.strftime('%Y')).first().time])
                start_date= start_date + relativedelta(years=1)
        return {"year": year}, 200
    elif int(parameters['month']) == 1:
        month = []
        start_date= this_date - relativedelta(months=int(parameters['month_n']))
        if start_date < rasp_date:
            start_date = rasp_date
            while start_date <= this_date:
                month.append([start_date.strftime('%Y-%m'), UsingTimeMonth.query.filter_by(key=rasp.key, date=start_date.strftime('%Y-%m')).first().time])
                start_date = start_date + relativedelta(months=1)
        else:
            while start_date <= this_date:
                month.append([start_date.strftime('%Y-%m'), UsingTimeMonth.query.filter_by(key=rasp.key, date=start_date.strftime('%Y-%m')).first().time])
                start_date= start_date + relativedelta(months=1)
        return {"month": month}, 200

    else:
        day = []
        start_date= this_date - relativedelta(days=int(parameters['day_n']))
        if start_date < rasp_date:
            start_date = rasp_date
            while start_date <= this_date:
                day.append([start_date.strftime('%Y-%m-%d'), UsingTimeDay.query.filter_by(key=rasp.key, date=start_date.strftime('%Y-%m-%d')).first().time])
                start_date= start_date + relativedelta(days=1)
        else:
            while start_date <= this_date:
                day.append([start_date.strftime('%Y-%m-%d'), UsingTimeDay.query.filter_by(key=rasp.key, date=start_date.strftime('%Y-%m-%d')).first().time])
                start_date= start_date + relativedelta(days=1)
        return {"day": day}, 200
    

@bp.route("/api/web/using-time/<string:year>")
def using_time_year(year):
    parameters = request.args
    rasp = Raspberry.query.filter_by(group=parameters['raspberry_group'], id=parameters['raspberry_id']).first()
    if rasp is None:
        return {"message":"라즈베리파이 정보가 없습니다."}, 404
    using_time = []
    for i in range(1, 13):
        date = year+"-"+"{:02d}".format(i)
        using_time_month = UsingTimeMonth.query.filter_by(key=rasp.key, date=date).first()
        if using_time_month is not None:
            using_time.append({date: using_time_month.time})
        else:
            using_time.append({date: 0})
    return {"using_time": using_time}, 200


@bp.route("/api/web/ranking")
def ranking():
    using_time_month = UsingTimeMonth.query.order_by(UsingTimeMonth.time.asc()).limit(10).all()
    ranking = []
    for u in using_time_month:
        rasp = Raspberry.query.get(u.key)
        ranking.append({"raspberry_id": rasp.id, "raspberry_group": rasp.group, "time": u.time})
    return {"ranking": ranking}, 200


@bp.route("/api/web/myranking")
@jwt_required
def myranking():
    myrasp = get_jwt_identity()
    using_time_month = UsingTimeMonth.query.order_by(UsingTimeMonth.time.asc()).all()
    rank = 1
    for u in using_time_month:
        if myrasp == u.key:
            return {"rank": rank, "total":len(using_time_month)}, 200
        rank = rank+1
