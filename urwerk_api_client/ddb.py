from urwerk_api_client import HTTPRequester


class TestsAPI(HTTPRequester):
    __sub_url = "tests"

    def send_test_report(self, secret, report):
        data = report
        headers = self._get_token_auth_header(secret)
        return self._post(url=(self.__sub_url, "reports/"), headers=headers, data=data)

    def send_test_results(self, secret, results):
        data = results
        headers = self._get_token_auth_header(secret)
        return self._post(url=(self.__sub_url, "results/"), headers=headers, data=data)


class DeviceAPI(HTTPRequester):
    __sub_url = "devices"

    def get_internal_device_id(self, secret, identity):
        params = {"identity": identity}
        headers = self._get_token_auth_header(secret)
        return self._get(url=self.__sub_url, headers=headers, params=params)[0]["id"]

    def _get_brand_id(self, secret, identity):
        params = {"identity": identity}
        headers = self._get_token_auth_header(secret)
        brand_url = self._get(url=self.__sub_url, headers=headers, params=params)[0]["brand"]
        # The brand url should end with "/api/brands/'brand_id'/" so that the following split will
        # succeed
        return brand_url.split('/')[-2]


class BrandAPI(HTTPRequester):
    __sub_url = "brands"

    def get_brand_name_by_id(self, secret, brand_id):
        headers = self._get_token_auth_header(secret)
        return self._get(url=(self.__sub_url, brand_id), headers=headers)["name"]


class DDBApi(DeviceAPI, BrandAPI, TestsAPI):

    def get_brand_name_by_identity(self, secret, identity):
        brand_id = self._get_brand_id(secret, identity)
        return self.get_brand_name_by_id(secret, brand_id)
