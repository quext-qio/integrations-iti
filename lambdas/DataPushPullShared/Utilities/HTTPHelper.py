from enum import Enum

import requests


class HTTPRequest(Enum):
    NONE = 0
    GET = 1
    POST = 2


def sendRequest(request_Type: HTTPRequest, _url: str, _data: str, _auth: str, _header: dict, _parameter: dict):
    response = {}
    if request_Type == HTTPRequest.GET:
        response = requests.get(_url, data=_data, auth=_auth, headers=_header, params=_parameter)
    else:
        response = requests.post(_url, data=_data, auth=_auth, headers=_header, params=_parameter)
    return response
