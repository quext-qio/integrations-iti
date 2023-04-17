from enum import Enum

import requests as requests


class HTTPRequest(Enum):
    NONE = 0
    GET = 1
    POST = 2


def sendRequest(request_Type: HTTPRequest, _url: str, _data: str, _auth: str, _header: dict):
    response = {}
    if request_Type == HTTPRequest.GET:
        response = requests.get(_url, auth=_auth, headers=_header)
    else:
        response = requests.post(_url, data=_data, auth=_auth, headers=_header)
    return response


class Method(Enum):
    NONE = 0
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
