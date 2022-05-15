import io
import warnings
import os
import collections
import re
import cgi
import codecs
from .version import __version__
from .structures import CaseInsensitiveDict
from .compat import quote, builtin_str, urlparse, urlunparse
from .exceptions import FileModeWarning, InvalidURL, InvalidHeader

def super_len(o):
    total_length = None
    current_position = 0

    if hasattr(o, '__len__'):
        total_length = len(o)

    elif hasattr(o, 'len'):
        total_length = o.len

    elif hasattr(o, 'fileno'):
        try:
            fileno = o.fileno()
        except io.UnsupportedOperation:
            pass
        else:
            total_length = os.fstat(fileno).st_size

            if 'b' not in o.mode:
                warnings.warn((
                    "Requests has determined the content-length for this "
                    "request using the binary size of the file: however, the "
                    "file has been opened in text mode (i.e. without the 'b' "
                    "flag in the mode). This may lead to an incorrect "
                    "content-length. In Requests 3.0, support will be removed "
                    "for files in text mode."),
                    FileModeWarning
                )

def to_key_val_list(value):

    if value is None:
        return None

    if isinstance(value, (str, bytes, bool, int)):
        raise ValueError('cannot encode objects that are not 2-tuples')

    if isinstance(value, collections.Mapping):
        value = value.items()

    return list(value)


def default_user_agent(name="python-requests"):
    """
    Return a string representing the default user agent.

    :rtype: str
    """
    return '%s/%s' % (name, __version__)

def default_headers():
    """
    :rtype: requests.structures.CaseInsensitiveDict
    """
    return CaseInsensitiveDict({
        'User-Agent': default_user_agent(),
        'Accept-Encoding': ', '.join(('gzip', 'deflate')),
        'Accept': '*/*',
        'Connection': 'keep-alive',
    })

def iter_slices(string, slice_length):
    """Iterate over slices of a string."""
    pos = 0
    if slice_length is None or slice_length <= 0:
        slice_length = len(string)
    while pos < len(string):
        yield string[pos:pos + slice_length]
        pos += slice_length

def stream_decode_response_unicode(iterator, r):
    if r.encoding is None:
        for item in iterator:
            yield item
        return

    decoder = codecs.getincrementaldecoder(r.encoding)(errors='replace')
    for chunk in iterator:
        rv = decoder.decode(chunk)
        if rv:
            yield rv
    rv = decoder.decode(b'', final=True)
    if rv:
        yield rv


_null = '\x00'.encode('ascii')  # encoding to ASCII for Python 3
_null2 = _null * 2
_null3 = _null * 3
def guess_json_utf(data):
    sample = data[:4]
    if sample in (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE):
        return 'utf-32'     # BOM included
    if sample[:3] == codecs.BOM_UTF8:
        return 'utf-8-sig'  # BOM included, MS style (discouraged)
    if sample[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        return 'utf-16'     # BOM included
    nullcount = sample.count(_null)
    if nullcount == 0:
        return 'utf-8'
    if nullcount == 2:
        if sample[::2] == _null2:   # 1st and 3rd are null
            return 'utf-16-be'
        if sample[1::2] == _null2:  # 2nd and 4th are null
            return 'utf-16-le'
        # Did not detect 2 valid UTF-16 ascii-range characters
    if nullcount == 3:
        if sample[:3] == _null3:
            return 'utf-32-be'
        if sample[1:] == _null3:
            return 'utf-32-le'
        # Did not detect a valid UTF-32 ascii-range character
    return None

def parse_header_links(value):
    links = []

    replace_chars = ' \'"'

    for val in re.split(', *<', value):
        try:
            url, params = val.split(';', 1)
        except ValueError:
            url, params = val, ''

        link = {'url': url.strip('<> \'"')}

        for param in params.split(';'):
            try:
                key, value = param.split('=')
            except ValueError:
                break

            link[key.strip(replace_chars)] = value.strip(replace_chars)

        links.append(link)

    return links


def get_encoding_from_headers(headers):
    content_type = headers.get('content-type')

    if not content_type:
        return None

    content_type, params = cgi.parse_header(content_type)

    if 'charset' in params:
        return params['charset'].strip("'\"")

    if 'text' in content_type:
        return 'ISO-8859-1'


def prepend_scheme_if_needed(url, new_scheme):
    scheme, netloc, path, params, query, fragment = urlparse(url, new_scheme)
    if not netloc:
        netloc, path = path, netloc

    return urlunparse((scheme, netloc, path, params, query, fragment))


UNRESERVED_SET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789-._~")
def unquote_unreserved(uri):
    parts = uri.split('%')
    for i in range(1, len(parts)):
        h = parts[i][0:2]
        if len(h) == 2 and h.isalnum():
            try:
                c = chr(int(h, 16))
            except ValueError:
                raise InvalidURL("Invalid percent-escape sequence: '%s'" % h)

            if c in UNRESERVED_SET:
                parts[i] = c + parts[i][2:]
            else:
                parts[i] = '%' + parts[i]
        else:
            parts[i] = '%' + parts[i]
    return ''.join(parts)

def requote_uri(uri):
    safe_with_percent = "!#$%&'()*+,/:;=?@[]~"
    safe_without_percent = "!#$&'()*+,/:;=?@[]~"
    try:
        return quote(unquote_unreserved(uri), safe=safe_with_percent)
    except InvalidURL:
        return quote(uri, safe=safe_without_percent)

_CLEAN_HEADER_REGEX_BYTE = re.compile(b'^\\S[^\\r\\n]*$|^$')
_CLEAN_HEADER_REGEX_STR = re.compile(r'^\S[^\r\n]*$|^$')

def check_header_validity(header):
    name, value = header

    if isinstance(value, bytes):
        pat = _CLEAN_HEADER_REGEX_BYTE
    else:
        pat = _CLEAN_HEADER_REGEX_STR
    try:
        if not pat.match(value):
            raise InvalidHeader("Invalid return character or leading space in header: %s" % name)
    except TypeError:
        raise InvalidHeader("Value for header {%s: %s} must be of type str or "
                            "bytes, not %s" % (name, value, type(value)))


## Functions in _internal_utils are put here for convinience 
def to_native_string(string, encoding='ascii'):
    if isinstance(string, builtin_str):
        out = string
    else:
        out = string.decode(encoding)

    return out

def unicode_is_ascii(u_string):
    assert isinstance(u_string, str)
    try:
        u_string.encode('ascii')
        return True
    except UnicodeEncodeError:
        return False
