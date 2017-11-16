import json
import http.client
import urllib.error
import urllib.request
from urllib.parse import urlencode


VERSION = "0.1.0"


class APIRequestError(IOError):
    """ exceptions raised by API requests """


class HTTPRequester:

    def __init__(self, api_url):
        self.root_url = api_url

    def _get_query_string_url(self, url, params):
        if params:
            assert isinstance(params, dict)
            encoded_params = urlencode(params)
            return "{}?{}".format(url, encoded_params)
        else:
            return url

    def _get(self, url=None, params=None):
        return self._get_response(self._get_query_string_url(url, params), "GET", None)

    def _put(self, url=None, data=None):
        return self._get_response(url, "PUT", json.dumps(data).encode("utf-8"))

    def _post(self, url=None, data=None):
        return self._get_response(url, "POST", json.dumps(data).encode("utf-8"))

    def _delete(self, url=None, params=None):
        return self._get_response(self._get_query_string_url(url, params), "DELETE", None)

    def _get_response(self, url_suffix, method, data):
        if url_suffix is None:
            path = ""
        elif isinstance(url_suffix, str):
            path = "/" + url_suffix
        else:
            path = "/" + "/".join(url_suffix)
        url = self.root_url + path
        request = urllib.request.Request(url=url, method=method, data=data)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as exc:
            raise APIRequestError("API Connect Error ({}): {}".format(url, exc)) from exc
        except urllib.error.HTTPError as exc:
            error_body = exc.fp.read()
            raise APIRequestError("API Error ({} -> {}): {}".format(url, exc, error_body)) from exc
        else:
            response_data = response.read()
            if response.status == http.client.OK:
                content = response_data.decode("utf-8")
                if not content:
                    # responses are never supposed to be empty
                    raise APIRequestError("API Empty Response Error: {}".format(url))
                json_string = json.loads(content)
                if json_string["errors"]:
                    raise APIRequestError("JSON encode error: {0} -> {1}"
                                          .format(url, json_string["errors"]))
                return json_string["data"]
            elif response.status == http.client.NO_CONTENT:
                return None
            else:
                raise APIRequestError("API status error ({} -> {} ({})): {}"
                                      .format(url, http.client.responses[response.status],
                                              response.status, response_data))
