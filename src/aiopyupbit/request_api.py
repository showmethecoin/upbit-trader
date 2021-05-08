# !/usr/bin/python
# -*- coding: utf-8 -*-
import re
import json
import aiohttp

getframe_expr = 'sys._getframe({}).f_code.co_name'


async def _parse_remaining_req(remaining_req):
    """

    :param remaining_req:
    :return:
    """
    try:
        p = re.compile("group=([a-z]+); min=([0-9]+); sec=([0-9]+)")
        m = p.search(remaining_req)
        return m.group(1), int(m.group(2)), int(m.group(3))
    except:
        return None, None, None


async def _call_public_api(url, **kwargs):
    """

    :param url:
    :param kwargs:
    :return:
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=kwargs) as response:
                remaining_req_dict = {}
                remaining_req = response.headers.get('Remaining-Req')
                if remaining_req is not None:
                    group, min, sec = await _parse_remaining_req(remaining_req)
                    remaining_req_dict['group'] = group
                    remaining_req_dict['min'] = min
                    remaining_req_dict['sec'] = sec
                contents = await response.json()
            return contents, remaining_req_dict

    # 요청 제한 횟수 초과시 발생하는 Json 디코딩 에러 처리
    except json.JSONDecodeError:
        return None
    except Exception as x:
        print("It failed", x.__class__.__name__)


# asyncio로 비동기 + 스레드풀 구현
async def _send_post_request(url, headers=None, data=None):
    """

    :param url:
    :param headers:
    :param data:
    :return:
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                remaining_req_dict = {}
                remaining_req = response.headers.get('Remaining-Req')
                if remaining_req is not None:
                    group, min, sec = await _parse_remaining_req(remaining_req)
                    remaining_req_dict['group'] = group
                    remaining_req_dict['min'] = min
                    remaining_req_dict['sec'] = sec
                contents = await response.json()
            return contents, remaining_req_dict

    except Exception as x:
        print("send post request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None


# asyncio로 비동기 + 스레드풀 구현
async def _send_get_request(url, headers=None, data=None):
    """

    :param url:
    :param headers:
    :return:
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, data=data) as response:
                remaining_req_dict = {}
                remaining_req = response.headers.get('Remaining-Req')
                if remaining_req is not None:
                    group, min, sec = await _parse_remaining_req(remaining_req)
                    remaining_req_dict['group'] = group
                    remaining_req_dict['min'] = min
                    remaining_req_dict['sec'] = sec
                contents = await response.json()
            return contents, remaining_req_dict
    except Exception as x:
        print("send get request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None


# asyncio로 비동기 + 스레드풀 구현
async def _send_delete_request(url, headers=None, data=None):
    """

    :param url:
    :param headers:
    :param data:
    :return:
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers, data=data) as response:
                remaining_req_dict = {}
                remaining_req = response.headers.get('Remaining-Req')
                if remaining_req is not None:
                    group, min, sec = await _parse_remaining_req(remaining_req)
                    remaining_req_dict['group'] = group
                    remaining_req_dict['min'] = min
                    remaining_req_dict['sec'] = sec
                contents = await response.json()
            return contents, remaining_req_dict
    except Exception as x:
        print("send delete request failed", x.__class__.__name__)
        print("caller: ", eval(getframe_expr.format(2)))
        return None
