from base64 import encodebytes
import json
import http.client
import urllib.error
import urllib.request
from urllib.parse import urlencode


VERSION = "0.4.0"


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

    def _get_auth_header(self, user, password):
        __secret = encodebytes("{}:{}".format(user, password).replace('\n', '').encode())
        return {"Authorization": "Basic {}".format(__secret.decode()).strip()}

    def _get_token_auth_header(self, token):
        return {"Authorization": "Token {}".format(token)}

    def _get(self, url=None, params=None, headers=None):
        return self._get_response(self._get_query_string_url(url, params), "GET", None, headers)

    def _put(self, url=None, data=None, headers=None):
        return self._get_response(url, "PUT", json.dumps(data).encode("utf-8"), headers)

    def _post(self, url=None, data=None, headers=None):
        if data:
            headers.update({"Content-Type": "application/json"})
        return self._get_response(url, "POST", json.dumps(data).encode("utf-8"), headers)

    def _delete(self, url=None, params=None, headers=None):
        return self._get_response(self._get_query_string_url(url, params), "DELETE", None, headers)

    def _get_response(self, url_suffix, method, data, headers):
        if url_suffix is None:
            path = ""
        elif isinstance(url_suffix, str):
            path = "/" + url_suffix
        else:
            path = "/" + "/".join(url_suffix)
        if headers is None:
            headers = {}
        url = self.root_url + path
        # Todo: correctly accept a 'permanently moved' (e.g. 301) status code
        request = urllib.request.Request(url=url, method=method, data=data, headers=headers)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as exc:
            raise APIRequestError("API Connect Error ({}): {}".format(url, exc)) from exc
        except urllib.error.HTTPError as exc:
            error_body = exc.fp.read()
            raise APIRequestError("API Error ({} -> {}): {}".format(url, exc, error_body)) from exc
        else:
            response_data = response.read()
            if response.status == http.client.OK or response.status == http.client.CREATED:
                content = response_data.decode("utf-8")
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
            elif response.status == http.client.NO_CONTENT:
                return None
            else:
                raise APIRequestError("API status error ({} -> {} ({})): {}"
                                      .format(url, http.client.responses[response.status],
                                              response.status, response_data))
