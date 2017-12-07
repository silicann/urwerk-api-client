from urwerk_api_client import HTTPRequester


class ReleasesAPI(HTTPRequester):

    __sub_url = "releases"

    def get_latest_firmware_build_id(self, sensor):
        params = {}
        params["available_for"] = sensor
        return self._get(url=self.__sub_url, params=params)["releases"][0]["id"]

    def get_latest_firmware_version(self, sensor):
        params = {}
        params["available_for"] = sensor
        return self._get(url=self.__sub_url, params=params)["releases"][0]["version"]
