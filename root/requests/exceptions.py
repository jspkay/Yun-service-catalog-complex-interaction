from urllib3.exceptions import HTTPError as BaseHTTPError

class RequestException(IOError):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop('response', None)
        self.response = response
        self.request = kwargs.pop('request', None)
        if (response is not None and not self.request and
                hasattr(response, 'request')):
            self.request = self.response.request
        super(RequestException, self).__init__(*args, **kwargs)

class WrongMethod(RequestException):
    def __init__(self, m):
        """No method such {} exist for http requests""".format(m)
        s = """No method such "{}" exist for http requests""".format(m)
        super(RequestException, self).__init__(s)
        print(s)

class HTTPError(RequestException):
    """An HTTP error occurred."""

class ChunkedEncodingError(RequestException):
    """The server declared chunked encoding but sent an invalid chunk."""

class ContentDecodingError(RequestException, BaseHTTPError):
    """Failed to decode response content"""


class StreamConsumedError(RequestException, TypeError):
    """The content for this response was already consumed"""

class Timeout(RequestException):
    """The request timed out.

    Catching this error will catch both
    :exc:`~requests.exceptions.ConnectTimeout` and
    :exc:`~requests.exceptions.ReadTimeout` errors.
    """

class RequestsWarning(Warning):
    """Base warning for Requests."""

class InvalidSchema(RequestException, ValueError):
    """See defaults.py for valid schemas."""

class InvalidURL(RequestException, ValueError):
    """The URL provided was somehow invalid."""

class InvalidHeader(RequestException, ValueError):
    """The header value provided was somehow invalid."""

class FileModeWarning(RequestsWarning, DeprecationWarning):
    """A file was opened in text mode, but Requests determined its binary length."""

class MissingSchema(RequestException, ValueError):
    """The URL schema (e.g. http or https) is missing."""

class ConnectTimeout(ConnectionError, Timeout):
    """The request timed out while trying to connect to the remote server.

    Requests that produced this error are safe to retry.
    """

class RetryError(RequestException):
    """Custom retries logic failed"""

class ReadTimeout(Timeout):
    """The server did not send any data in the allotted amount of time."""
