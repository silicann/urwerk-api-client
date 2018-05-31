from functools import lru_cache

from urwerk_api_client import HTTPRequester


class UserAPI(HTTPRequester):
    # TODO: maybe the user api is not "finished" yet ... it was not documented
    #       so there may need to be things changed

    # TODO: wrong suffix
    __sub_url = "system"

    def get_users(self):
        return self._get()

    def get_user_by_name(self, user_name):
        return self._get(url=(self.__sub_url, user_name))

    def post_user(self, data):
        return self._post(url=self.__sub_url, data=data)

    def change_user(self, user_name, data):
        return self._put(url=(self.__sub_url, user_name), data=data)

    def delete_user(self, user_name):
        return self._delete(url=(self.__sub_url, user_name))


class SettingsAPI(HTTPRequester):

    __sub_url = "settings"

    def settings_reset(self):
        return self._delete(url=self.__sub_url)


class SystemAPI(HTTPRequester):

    __sub_url = "system"

    def get_hostname(self):
        return self.get_system()["hostname"]

    def set_hostname(self, hostname):
        return self.change_system({"hostname": hostname})

    def reboot(self):
        return self._post(url=(self.__sub_url, "reboot"))

    def factory_reset(self):
        return self._post(url=(self.__sub_url, "factory-reset"))

    def get_system(self):
        return self._get(url=self.__sub_url)

    def change_system(self, data):
        return self._put(url=self.__sub_url, data=data)

    def get_system_time(self):
        return self._get(url=(self.__sub_url, "time"))

    def change_system_time(self, data):
        return self._put(url=(self.__sub_url, "time"), data=data)

    @lru_cache()
    def get_system_time_zones(self):
        return self._get(url=(self.__sub_url, "time/zones"))


class FirmwareAPI(HTTPRequester):

    __sub_url = "firmware"

    def _get_firmware_status(self):
        return self._get(url=(self.__sub_url, "status"))

    def get_firmware_version(self):
        return self._get_firmware_status()["version"]

    def get_firmware_source_url(self):
        return self._get_firmware_status()["source_url"]

    def upgrade_recovery_image(self):
        return self._post(url=(self.__sub_url, "recovery", "upgrade-from-current"))

    def get_current_recovery_build_id(self):
        return self._get(url=(self.__sub_url, "recovery"))["id"]

    def get_current_build_id(self):
        return self._get(url=(self.__sub_url, "status"))["build_id"]


class NetworkAPI(HTTPRequester):

    __sub_url = "network"

    def get_network_interfaces(self):
        interfaces = self._get(url=(self.__sub_url, "interfaces"))["network_interfaces"]
        interfaces.sort(key=lambda item: item["iface"])
        return interfaces

    def get_network_interface_by_name(self, name):
        return self._get(url=(self.__sub_url, "interfaces", name))["network_interface"]

    def set_network_interface_address_in_domain(self, network_interface_name, address_domain,
                                                address_configurations):
        """ reconfigure the address configurations of an interface in the given domain

        The other address domain remains unchanged.
        Changes are applied immediately.

        @param domain: "ipv4" or "ipv6"
        """
        assert address_domain in ("ipv4", "ipv6")
        data = {address_domain: {"address_configurations": address_configurations}}
        return self._put(url=(self.__sub_url, "interfaces", network_interface_name),
                         data=data)["network_interface"]

    def reset_network_settings_to_defaults(self):
        return self._delete(url=self.__sub_url)


class OutputsAPI(HTTPRequester):

    __sub_url = "peripherals/outputs"

    def set_output_mode(self, mode):
        data = {"output_driver": mode}
        return self._put(url=self.__sub_url, data=data)['output_driver']

    def get_output_mode(self):
        return self._get(url=self.__sub_url)['output_driver']


class KeypadAPI(HTTPRequester):

    __sub_url = "peripherals/keypad"

    def get_keypad_lock_state(self):
        return self._get(url=self.__sub_url)["locked"]

    def set_keypad_lock_state(self, state):
        return self._put(url=self.__sub_url, data={"locked": bool(state)})


class DeviceAPI(HTTPRequester):

    __sub_url = "device"

    @lru_cache()
    def _get_device_info(self):
        return self._get(url=self.__sub_url)

    def get_device_id(self):
        return self._get_device_info()["device_id"]

    def get_device_model_key(self):
        return self._get_device_info()["model_key"]

    def get_device_model_name(self):
        return self._get_device_info()["model"]

    def get_device_variant(self):
        return self._get_device_info().get("variant", None)

    def get_device_vendor_name(self):
        return self._get_device_info()["vendor"]


class CapabilitiesAPI(HTTPRequester):

    __sub_url = "sensor/capabilities"

    @lru_cache()
    def _get_capabilities(self):
        return self._get(url=self.__sub_url)

    def get_output_pin_count(self):
        return self._get_capabilities()["output_pin_count"]

    def get_trigger_sources(self):
        return self._get_capabilities()["trigger_sources"]


class DetectionProfilesAPI(HTTPRequester):

    __sub_url = "sensor/detection-profiles"

    def get_detection_profiles(self):
        return self._get(url=self.__sub_url)

    def get_current_detection_profile(self):
        return self._get(url=(self.__sub_url, "current"))

    def get_detection_profile_by_uuid(self, uuid):
        return self._get(url=(self.__sub_url, uuid))

    def post_detection_profile(self, data):
        return self._post(url=self.__sub_url, data=data)

    def change_detection_profile(self, uuid, data):
        return self._put(url=(self.__sub_url, uuid), data=data)

    def delete_detection_profile(self, uuid):
        return self._delete(url=(self.__sub_url, uuid))

    def run_autogain(self, minimum_sample_rate=None, target_level=None):
        params = {}
        if minimum_sample_rate is not None:
            params["minimum_sample_rate"] = minimum_sample_rate
        if target_level is not None:
            params["level"] = target_level
        return self._post(url=(self.__sub_url, "current", "autogain"), data=params)

    def set_white_reference(self, profile_id="current"):
        self._post(url=(self.__sub_url, profile_id, "white-reference"))

    def factory_reset_white_reference(self, profile_id="current"):
        self._delete(url=(self.__sub_url, profile_id, "white-reference"))

    def get_profile_normalization_constants(self, profile_id="current"):
        """ Get normalization constants used in the given detection profile.

        The result can be different from the result of the get_factory_calibration_constants()
        function from the ConstantsMaintenanceAPI, that returns the normalization constants stored
        in EEPROM.
        """
        return self._get(url=(self.__sub_url, profile_id))["normalization_constant"]

    def enable_compensation(self, profile_id="current"):
        """ Enable the transformation of colorvalues to reduce inter-sensor variability for the
        given profile.

        Application of the transformation of colorvalues requires the availability of
        sensor-specific constants on the device. """
        params = {'compensation_settings': {'use_calibration_samples': True}}
        return self._put(url=(self.__sub_url, profile_id), data=params)

    def disable_compensation(self, profile_id="current"):
        """ Disable the transformation of colorvalues to reduce inter-sensor variability for the
        given profile."""

        params = {'compensation_settings': {'use_calibration_samples': False}}
        return self._put(url=(self.__sub_url, profile_id), data=params)


class DetectablesAPI(HTTPRequester):

    __sub_url = "sensor/detectables"

    def get_detectables(self, profile=None, matcher_id=None):
        """ return all detectables sorted by UUID """
        params = {}
        if profile is not None:
            params["profile_id"] = profile
        if matcher_id is not None:
            params["matcher_id"] = matcher_id
        detectables = self._get(url=self.__sub_url, params=params)["detectables"]
        detectables.sort(key=lambda item: item["uuid"])
        return detectables

    def get_detectable_by_uuid(self, uuid, profile=None):
        params = None if profile is None else {"profile_id": profile}
        return self._get(url=(self.__sub_url, uuid), params=params)

    def post_detectable(self, profile=None, data=None):
        data = {} if data is None else dict(data)
        if profile is not None:
            data["profile_id"] = profile
        return self._post(url=self.__sub_url, data=data)

    def change_detectable(self, uuid, data, profile=None):
        data = {} if data is None else dict(data)
        if profile is not None:
            data["profile_id"] = profile
        return self._put(url=(self.__sub_url, uuid), data=data)

    def delete_detectable(self, uuid, profile=None):
        params = {} if profile is None else {"profile_id": profile}
        return self._delete(url=(self.__sub_url, uuid), params=params)

    def delete_detectables(self, profile=None, matcher_id=None):
        params = {}
        if profile is not None:
            params["profile_id"] = profile
        if matcher_id is not None:
            params["matcher_id"] = matcher_id
        return self._delete(url=(self.__sub_url), params=params)


class EmitterAPI(HTTPRequester):

    __sub_url = "sensor/emitters"

    def get_emitters(self, profile=None):
        params = None if profile is None else {"profile_id": profile}
        return self._get(url=self.__sub_url, params=params)

    def get_emitter_by_id(self, hid, profile=None):
        params = None if profile is None else {"profile_id": profile}
        return self._get(url=(self.__sub_url, hid), params=params)

    def change_emitter(self, uuid, data, profile=None):
        data = {} if data is None else dict(data)
        if profile is not None:
            data["profile_id"] = profile
        return self._put(url=(self.__sub_url, uuid), data=data)


class MatcherAPI(HTTPRequester):

    __sub_url = "sensor/matchers"

    def get_matchers(self, profile=None):
        """ return all matchers sorted by UUID """
        params = None if profile is None else {"profile_id": profile}
        matchers = self._get(url=self.__sub_url, params=params)["matchers"]
        matchers.sort(key=lambda item: item["uuid"])
        return matchers

    def get_matcher_by_uuid(self, uuid, profile=None):
        params = None if profile is None else {"profile_id": profile}
        return self._get(url=(self.__sub_url, uuid), params=params)

    def post_matcher(self, profile=None, data=None):
        data = {} if data is None else dict(data)
        if profile is not None:
            data["profile_id"] = profile
        return self._post(url=self.__sub_url, data=data)

    def change_matcher(self, uuid, data, profile=None):
        data = {} if data is None else dict(data)
        if profile is not None:
            data["profile_id"] = profile
        return self._put(url=(self.__sub_url, uuid), data=data)

    def delete_matcher(self, uuid, profile=None):
        params = {} if profile is None else {"profile_id": profile}
        return self._delete(url=(self.__sub_url, uuid), params=params)

    def delete_matchers(self):
        return self._delete(url=self.__sub_url)

    def set_matcher_output_pattern(self, uuid, pattern):
        data = {'output_pattern': {'states': pattern}}
        return self._put(url=(self.__sub_url, uuid), data=data)

    def get_matcher_output_pattern(self, uuid):
        return self._get(url=(self.__sub_url, uuid))


class SamplesAPI(HTTPRequester):

    __sub_url = "sensor/samples"

    def get_current_sample(self):
        return self._get(url=(self.__sub_url, "current"))

    def get_sample_stream(self, count=None, format=None, delimiter=None):
        params = dict(stream=1)
        if count:
            params['stream_count'] = count
        if format:
            params['format'] = format
        if delimiter:
            params['delimiter'] = delimiter
        yield from self._get(url=self.__sub_url, params=params, handler=self._stream_response)


class ColorspacesAPI(HTTPRequester):

    __sub_url = "sensor/colorspaces"

    def get_colorspace(self):
        return self.get_current_detection_profile()["colorspace"]

    def set_colorspace(self, colorspace_id):
        return self.change_detection_profile("current",
                                             {"colorspace": {"space_id": colorspace_id}})

    @lru_cache()
    def get_colorspaces(self):
        return self._get(url=self.__sub_url)["colorspaces"]

    def get_colorspace_by_name(self, name):
        return self._get(url=(self.__sub_url, name))


class ConstantsMaintenanceAPI(HTTPRequester):
    __sub_url = "maintenance/constants"

    def get_factory_calibration_constants(self, secret):
        headers = self._get_auth_header("production-msh", secret)
        return self._get(url=(self.__sub_url, "calibration-samples"), headers=headers)["values"]

    def get_factory_normalization_constants(self, secret):
        headers = self._get_auth_header("production-msh", secret)
        return self._get(url=(self.__sub_url, "normalization"), headers=headers)["values"]

    def set_factory_normalization_constants(self, secret, normalization_constants):
        if isinstance(normalization_constants, list) and len(normalization_constants) == 3:
            data = {"values": normalization_constants}
        else:
            # Todo: Vielleicht lieber eine Fehlermeldung werfen als einfach die vorhandenen Werte
            # nochmal setzen?
            data = {"values": self.get_normalization_constants(secret)}
        headers = self._get_auth_header("production-msh", secret)
        return self._put(url=(self.__sub_url, "normalization"), headers=headers,
                         data=data)["values"]

    def set_factory_calibration_constants(self, secret, calibration_constants):
        if isinstance(calibration_constants, list) and len(calibration_constants) == 48:
            data = {"values": calibration_constants}
        else:
            # Todo: Vielleicht lieber eine Fehlermeldung werfen als einfach die vorhandenen Werte
            # nochmal setzen?
            data = {"values": self.get_calibration_constants(secret)}
        headers = self._get_auth_header("production-msh", secret)
        return self._put(url=(self.__sub_url, "calibration-samples"), headers=headers,
                         data=data)["values"]


class DefaultsAPI(HTTPRequester):
    __sub_url = "defaults"

    def set_default(self, object_type, key, value):
        self._post(self.__sub_url, data={
            'object_type': object_type,
            'key': key,
            'value': value
        })

    def get_defaults(self):
        return self._get(self.__sub_url)['defaults']

    def get_factory_defaults(self):
        return self._get(self.__sub_url)['factory_defaults']

    def get_default(self, object_type, key):
        def _find(*collections, test):
            for collection in collections:
                for obj in collection():
                    if test(obj):
                        return obj
        return _find(self.get_defaults, self.get_factory_defaults,
                     test=lambda d, o=object_type, k=key: d['object_type'] == o and d['key'] == k)


class ServiceMaintenanceAPI(HTTPRequester):
    __sub_url = "maintenance/services"

    def enable_service(self, secret, service):
        headers = self._get_auth_header("production-msh", secret)
        return self._post(url=(self.__sub_url, service), headers=headers)

    def disable_service(self, secret, service):
        headers = self._get_auth_header("production-msh", secret)
        return self._delete(url=(self.__sub_url, service), headers=headers)


class ColorsensorAPI(DetectablesAPI, DefaultsAPI, DetectionProfilesAPI, EmitterAPI, MatcherAPI,
                     NetworkAPI, SamplesAPI, SystemAPI, DeviceAPI, CapabilitiesAPI, UserAPI,
                     ColorspacesAPI, KeypadAPI, SettingsAPI, FirmwareAPI, ConstantsMaintenanceAPI,
                     ServiceMaintenanceAPI, OutputsAPI):
    """API Client for all features of a colorsensor"""
