from base64 import encodebytes
import enum
import functools
import http.client
import json
import urllib.error
from urllib.parse import urlencode
import urllib.request

VERSION = "0.17.1"


class APIRequestError(IOError):
    """ exceptions raised by API requests """


class APIAuthenticationError(APIRequestError):
    """ raised in case an action is only available after authentication """


class APIAuthorizationError(APIRequestError):
    """ raised in case an action requires authentication and the provided credentials
    are not sufficient """


def encode_data():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, data=None, headers=None, **kwargs):
            if data:
                headers = dict(headers) if headers is not None else {}
                if isinstance(data, bytes):
                    headers.setdefault("Content-Type", "application/octet-stream")
                else:
                    headers.setdefault("Content-Type", "application/json")
                    data = json.dumps(data).encode("UTF-8")
            return func(*args, data=data, headers=headers, **kwargs)
        return wrapper
    return decorator


def _handle_request(url, method, data, headers, handler, user_agent=None):
    headers = dict(headers) if headers is not None else {}
    if user_agent is not None:
        headers.setdefault("User-Agent", user_agent)
    # Todo: correctly accept a 'permanently moved' (e.g. 301) status code
    request = urllib.request.Request(url=url, method=method, data=data, headers=headers)
    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as exc:
        error_body = exc.fp.read()
        error_type = {
            401: APIAuthenticationError,
            403: APIAuthorizationError
        }.get(exc.code, APIRequestError)
        raise error_type("API Error ({} -> {}): {}".format(url, exc, error_body)) from exc
    except urllib.error.URLError as exc:
        raise APIRequestError("API Connect Error ({}): {}".format(url, exc)) from exc
    else:
        def unpack_data(data):
            content = data.decode("utf-8")
            if not content:
                # responses are never supposed to be empty
                raise APIRequestError("API Empty Response Error: {}".format(url))
            json_string = json.loads(content)
            # The ddb does not send "errors" (yet?)
            if "errors" in json_string.keys() and json_string["errors"]:
                raise APIRequestError("JSON encode error: {0} -> {1}"
                                      .format(url, json_string["errors"]))
            if "results" in json_string.keys():  # ddb
                return json_string["results"]
            elif "data" in json_string.keys():  # schall, colorsensor
                return json_string["data"]
            else:  # ddb
                return json_string

        if response.status == http.client.OK or response.status == http.client.CREATED:
            return handler(response, unpack_data)
        elif response.status == http.client.NO_CONTENT:
            return None
        else:
            raise APIRequestError("API status error ({} -> {} ({})): {}"
                                  .format(url, http.client.responses[response.status],
                                          response.status, response.read()))


class HTTPRequester:
    def __init__(self, api_url, user_agent=None):
        self.root_url = api_url.rstrip("/")
        self._user_agent = user_agent if user_agent else "urwerk-api-client/{}".format(VERSION)

    def get_user_agent(self):
        return self._user_agent

    def _get_url(self, url, params):
        if isinstance(url, tuple):
            url = "/".join(url)
        if params:
            assert isinstance(params, dict)
            encoded_params = urlencode(params)
            url = "{}?{}".format(url, encoded_params)
        if url is None:
            path = ""
        else:
            path = "/" + url
        return self.root_url + path

    def _get_auth_header(self, user, password):
        __secret = encodebytes("{}:{}".format(user, password).replace('\n', '').encode())
        return {"Authorization": "Basic {}".format(__secret.decode()).strip()}

    def _get_token_auth_header(self, token):
        return {"Authorization": "Token {}".format(token)}

    def _get(self, url=None, params=None, headers=None, handler=None):
        return (handler or self._get_response)(
            self._get_url(url, params), "GET", None, headers=headers)

    @encode_data()
    def _put(self, url=None, data=None, headers=None, handler=None):
        return (handler or self._get_response)(
            self._get_url(url, None), "PUT", data, headers=headers)

    @encode_data()
    def _post(self, url=None, data=None, headers=None, handler=None):
        return (handler or self._get_response)(
            self._get_url(url, None), "POST", data, headers=headers)

    def _delete(self, url=None, params=None, headers=None, handler=None):
        return (handler or self._get_response)(
            self._get_url(url, params), "DELETE", None, headers=headers)

    def _get_response(self, url, method, data, headers=None):
        def handler(res, unpacker):
            return unpacker(res.read())

        return _handle_request(url, method, data, headers, handler, user_agent=self._user_agent)

    def _stream_response(self, url, method, data, headers=None):
        def handler(res, unpacker):
            for data in res:
                yield unpacker(data)

        yield from _handle_request(
            url, method, data, headers, handler, user_agent=self._user_agent)


class IPProtocol(enum.Enum):
    v4 = ('ipv4', 4, 'IPv4')
    v6 = ('ipv6', 6, 'IPv6')

    @property
    def id(self):
        return self.value[0]

    @property
    def version(self):
        return self.value[1]

    @property
    def label(self):
        return self.value[2]
