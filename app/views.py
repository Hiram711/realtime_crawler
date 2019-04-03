from flask import Blueprint, jsonify, g, request
from .auth import auth
from .uitls import sync_data
from asyncio import TimeoutError
import asyncio
from datetime import datetime, timedelta
from .caching import cache
from itertools import groupby

main_bp = Blueprint('main', __name__)

index_info = {
    '/token': 'get a token for auth',
    '/rmhnair/realtime?beginDate=2018-01-01&endDate=2018-01-05&dep=KMG&arv=SHA': 'get realtime data'
}


def cache_sync_data(being_date_str, end_date_str, dep_code, arv_code):
    begin_date = datetime.strptime(being_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    l_keys = ((begin_date + timedelta(days=i)).strftime('%Y-%m-%d') + dep_code + arv_code for i in
              range((end_date - begin_date).days + 1))
    data_by_day = []
    l_key_not_find = []
    for key in l_keys:
        data = cache.get(key)
        if data:
            data_by_day.append(dict(key=key, data=data))
        else:
            l_key_not_find.append(key[:10])

    ls_key_not_find = [
        (
            datetime.strptime(l_key_not_find[i], '%Y-%m-%d'),
            datetime.strptime(l_key_not_find[0], '%Y-%m-%d') + timedelta(days=i)
        )
        for i in range(len(l_key_not_find))
    ]
    for k1, g1 in groupby(ls_key_not_find, lambda x: (x[1] - x[0]).days):
        lg = [k for k, v in g1]
        data = sync_data(datetime.strftime(min(lg), '%Y-%m-%d'), datetime.strftime(max(lg), '%Y-%m-%d'), dep_code,
                         arv_code)
        for i in data:
            cache.set(i['key'], i['data'], timeout=10 * 60)
            data_by_day.append(i)
    return data_by_day


@main_bp.route('/')
def index():
    return index_info


@main_bp.route('/rmhnair/realtime')
@auth.login_required
def rmhnair_realtime():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    dt1 = request.values.get('beginDate')
    dt2 = request.values.get('endDate')
    dep_code = request.values.get('dep')
    arv_code = request.values.get('arv')
    try:
        # data = sync_data(dt1, dt2, dep_code, arv_code)
        data = cache_sync_data(dt1, dt2, dep_code, arv_code)
        return data
    except TimeoutError as e:
        response = jsonify({'error': 'Gateway Timeout', 'message': 'Sync data failed,please retry'})
        response.status_code = 504
        return response


@main_bp.route('/token')
@auth.login_required
def get_token():
    if g.current_user is None or g.token_used:
        response = jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials'})
        response.status_code = 401
        return response
    return {'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600}
