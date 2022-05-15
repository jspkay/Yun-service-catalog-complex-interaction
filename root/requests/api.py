from . import session as s

def request(method, url, **kwargs):

    with s.Session() as session:
        return session.request(method=method, url=url, **kwargs)

def get(url, params=None, **kwargs):
    return request('get', url, **kwargs)

def post(url, data=None, **kwargs):
    return request('post', url, **kwargs)

def put(url, data=None, **kwargs):
    return request('put', url, **kwargs)

def delete(url, data=None, **kwargs):
    return request('delete', url, **kwargs)