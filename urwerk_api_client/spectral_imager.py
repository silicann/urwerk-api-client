from urwerk_api_client import HTTPRequester
from urwerk_api_client.colorsensor import ColorsensorAPI


class SpectralAPI(HTTPRequester):

    __sub_url = "sensor/spectral"

    def _get_spectral_sample(self):
        return self._get(url=(self.__sub_url, "sample"))

    def get_spectral_sampling_settings(self, profile_id="current"):
        return self.get_detection_profile_by_uuid(profile_id)["sampling_settings"]

    def get_spectrum(self):
        """returns array of [wavelength, measured value]"""
        return self._get_spectral_sample()["spectrum"]

    def get_spectrum_dict(self):
        """returns array of point-dictionaries: [{"wavelength": 100.0, "value": 0.01}, ...]"""
        spectrum = self.get_spectrum()
        return [{"wavelength": point[0], "value": point[1]} for point in spectrum]

    def get_wavelengths(self):
        """returns array of used wavelengths"""
        return self._get(url=(self.__sub_url, "wavelengths"))["wavelengths"]

    def reset_spectral_dark_reference(self):
        return self._delete(url=(self.__sub_url, "dark-reference"))

    def set_spectral_dark_reference(self):
        return self._post(url=(self.__sub_url, "dark-reference"))

    def get_average_count(self, profile_id="current"):
        return self.get_spectral_sampling_settings(profile_id)["average_count"]

    def set_average_count(self, average_count, profile_id="current"):
        data = {"sampling_settings": {"average_count": average_count}}
        return self.change_detection_profile(profile_id, data)

    def get_integration_time(self, profile_id="current"):
        return self.get_spectral_sampling_settings(profile_id)["integration_time"]

    def set_integration_time(self, integration_time, profile_id="current"):
        data = {"sampling_settings": {"integration_time": integration_time}}
        return self.change_detection_profile(profile_id, data)

    def spectral_normalize(self):
        return self._post(url=(self.__sub_url, "normalization"))

    def spectral_reset_normalization(self):
        return self._delete(url=(self.__sub_url, "normalization"))

    def get_regions_of_interest(self):
        """
        returns an array of dictionaries where each dictionary contains two points:
        x_min, y_min => point with lowest measured value
        x_max, y_max => point with highest measured value
        => both points are within one of the previously set regions of interest
        => x represents the wavelength and y represents the value of each point

        example output: [{'y_min': 0.108, 'x_min': 400.071, 'y_max': 0.802, 'x_max': 438.688}]
        => minimal value in region is 0.108 at wavelength 400.071
        => maximal value in region is 0.802 at wavelength 438.688
        """
        return self._get_spectral_sample()["regions_of_interest"]

    def set_regions_of_interest(self, boundaries=None):
        """
        boundaries:
            array of (lower_bound, upper_bound)
            or array of {"lower_boundary": float, "upper_boundary": float}
        example usage:
            set_regions_of_interest(
                [(0.0, 100.0), (50.0, 250.0)]
            )
        """
        data = {}
        if boundaries is not None:
            data["boundaries"] = boundaries
        return self._post(url=(self.__sub_url, "regions-of-interest"), data=data)


class SpectralImagerAPI(SpectralAPI, ColorsensorAPI):
    """API Client for some features of a spectral imager"""
