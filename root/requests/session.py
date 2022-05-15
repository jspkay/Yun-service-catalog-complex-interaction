from collections import Mapping
from datetime import timedelta
import time
from .models import Request, PreparedRequest
from .compat import OrderedDict
from .utils import to_key_val_list, default_headers
from .structures import CaseInsensitiveDict
from .exceptions import InvalidSchema
from .adapters import HTTPAdapter

def merge_setting(request_setting, session_setting, dict_class=OrderedDict):
    """Determines appropriate setting for a given request, taking into account
    the explicit setting on that request, and the setting in the session. If a
    setting is a dictionary, they will be merged together using `dict_class`
    """

    if session_setting is None:
        return request_setting

    if request_setting is None:
        return session_setting

    # Bypass if not a dictionary (e.g. verify)
    if not (
            isinstance(session_setting, Mapping) and
            isinstance(request_setting, Mapping)
    ):
        return request_setting

    merged_setting = dict_class(to_key_val_list(session_setting))
    merged_setting.update(to_key_val_list(request_setting))

    # Remove keys that are set to None. Extract keys first to avoid altering
    # the dictionary during iteration.
    none_keys = [k for (k, v) in merged_setting.items() if v is None]
    for key in none_keys:
        del merged_setting[key]

    return merged_setting

class Session:

    def __init__(self):
        self.headers = default_headers()
        self.params = {}

        self.adapters = OrderedDict()
        self.mount('http://', HTTPAdapter())

    def prepare_request(self, request):
        p = PreparedRequest()
        p.prepare(
            method=request.method.upper(),
            url=request.url,
            files=request.files,
            data=request.data,
            json=request.json,
            headers=merge_setting(request.headers, self.headers, dict_class=CaseInsensitiveDict),
            params=merge_setting(request.params, self.params),
        )
        return p

    def request(self, method, url,
            params=None, data=None, headers=None, cookies=None, files=None,
            auth=None, timeout=None, allow_redirects=True, proxies=None,
            hooks=None, stream=None, verify=None, cert=None, json=None):

        req = Request(
                method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {}
        )
        prep = self.prepare_request(req)

        # Send the request
        resp = self.send(prep)

        return resp

    def send(self, request, **kwargs):

        if isinstance(request, Request):
            raise ValueError('You can only send PreparedRequests.')

        adapter = self.get_adapter(url=request.url)        
        preferred_clock = time.time
        start = preferred_clock()
        r = adapter.send(request, **kwargs)
        elapsed = preferred_clock() - start

        r.elapsed = timedelta(seconds=elapsed)

        return r

    def get_adapter(self, url):
        for (prefix, adapter) in self.adapters.items():

            if url.lower().startswith(prefix):
                return adapter

        # Nothing matches :-/
        raise InvalidSchema("No connection adapters were found for '%s'" % url)

    def close(self):
        for v in self.adapters.values():
            v.close()

    def mount(self, prefix, adapter):
        self.adapters[prefix] = adapter
        keys_to_move = [k for k in self.adapters if len(k) < len(prefix)]

        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)
    
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()