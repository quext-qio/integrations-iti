from enum import Enum

import requests

from PeriodicShared.Model.Periodic import Periodic


class HTTPRequest(Enum):
    NONE = 0
    GET = 1
    POST = 2


def sendRequest(request_Type: HTTPRequest, _data: str, _auth: str, _header: dict):
    response = {}
    if request_Type == HTTPRequest.GET:
        response = requests.get(Periodic.URL, data=_data, auth=_auth, headers=_header)
    else:
        response = requests.post(Periodic.URL, data=_data, auth=_auth, headers=_header)
    return response


class Method(Enum):
    NONE = 0
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
