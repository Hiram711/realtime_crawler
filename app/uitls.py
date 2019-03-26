import asyncio
import json
from datetime import datetime, timedelta

import aiohttp
import js2py
from flask import jsonify
from werkzeug.wrappers import Response
from itertools import groupby
from operator import itemgetter


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8');
        return json.JSONEncoder.default(self, obj)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)
        return super(JsonResponse, cls).force_type(response, environ)


async def _sync_data(being_date_str, end_date_str, dep_code, arv_code):
    async with aiohttp.ClientSession() as session:
        async with session.get('http://10.42.11.226:5020/rmhnair/random', timeout=30) as resp:
            if resp.status == 200:
                cookies = await resp.text()
                cookies = json.loads(cookies)
                target_url = 'http://rm.hnair.com/ajax/Yeesky.EIM.Site.BI.ClassTune.AjaxClass.FlightTuneAjax,Yeesky.EIM.Site.BI.ClassTune.ashx?_method=CollectData&_session=r'
                headers = {'Host': 'rm.hnair.com',
                           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0',
                           'Accept': '*/*',
                           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                           'Accept-Encoding': 'gzip, deflate',
                           'Referer': 'http://rm.hnair.com/BI/ClassTune/WebUI/FlightTune.aspx',
                           'Content-Type': 'text/plain;charset=UTF-8',
                           'Connection': 'keep-alive',
                           }
                param_reg = 'flightStaDate={}\r\nflightEndDate={}\r\nflightTime1=00:00\r\nflightTime2=23:59\r\nsegment={}'
                param = param_reg.format(being_date_str, end_date_str, dep_code + arv_code)
                async with session.post(url=target_url, cookies=cookies, headers=headers, data=param,
                                        timeout=60) as resp:
                    if resp.status == 200:
                        result = await resp.text()
                        test_data = js2py.eval_js('var data=%s;var data1=JSON.stringify(data);data1' % result)
                        js_data = json.loads(test_data)
                        rs_data = js_data['Tables'][1].get('Rows')
                        return rs_data


def sync_data(being_date_str, end_date_str, dep_code, arv_code):
    start = datetime.now()
    begin_date = datetime.strptime(being_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    l_param = []
    while True:
        if begin_date + timedelta(days=6) < end_date:
            l_param.append((begin_date.strftime('%Y-%m-%d'), (begin_date + timedelta(days=6)).strftime('%Y-%m-%d')))
            begin_date += timedelta(days=7)
        else:
            l_param.append((begin_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            break
    loop = asyncio.get_event_loop()
    tasks = [asyncio.ensure_future(_sync_data(i[0], i[1], dep_code, arv_code)) for i in l_param]
    loop.run_until_complete(asyncio.wait(tasks))

    l_data = []
    for task in tasks:
        task_result = task.result()
        if task_result:
            for row in task_result:
                l_data.append(row)
    l_data.sort(key=itemgetter('FLIGHT_DATE'))
    rs = []
    for key, group in groupby(l_data, itemgetter('FLIGHT_DATE')):
        rs.append(dict(key=key + dep_code + arv_code, data=list(group)))
    return rs


if __name__ == '__main__':
    dt1 = datetime.now().strftime('%Y-%m-%d')
    dt2 = (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d')
    data = sync_data(dt1, dt2, 'KMG', 'SHA')
    print(data)
