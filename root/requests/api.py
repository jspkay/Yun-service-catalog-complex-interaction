import imp
from . import session as s
import urllib3 as ul
import json
from .models import Response
from .exceptions import WrongMethod

def request(method, url, **kwargs):
    if method == "post" or method == "POST":
    	method = "POST"
    elif method == "PUT" or method == "put":
    	method = "PUT"
    elif method == "delete" or method == "DELETE":
    	method = "DELETE"
    else:
    	raise WrongMethod(method)
    
    if method != "GET":
        if kwargs["data"]:
            data_encoded = json.dumps(kwargs["data"])
        elif kwargs["json"]:
            data_encoded = json.dumps(kwargs["json"])
        http = ul.PoolManager()
        r = http.request("POST", url, body=data_encoded)
        
        response = Response()
        response.encoding = "utf-8"
        response.headers = r.headers;
        response.status_code = r.status
        response._content = r.data
        
        return response

    with s.Session() as session:
        return session.request(method=method, url=url, **kwargs)

def get(url, params=None, **kwargs):
    return request('get', url, params=params, **kwargs)

def post(url, data=None, **kwargs):
    return request('post', url, data=data, **kwargs)

def put(url, data=None, **kwargs):
    return request('put', url, data=data, **kwargs)

def delete(url, data=None, **kwargs):
    return request('delete', url, data=data, **kwargs)
