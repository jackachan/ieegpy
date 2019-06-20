##################################################################################
# Copyright 2013-19 by the Trustees of the University of Pennsylvania
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##################################################################################


import xml.etree.ElementTree as ET
from deprecation import deprecated
from ieeg.dataset import Dataset as DS, IeegConnectionError
from ieeg.ieeg_api import IeegApi

class Session:
    """
    Class representing Session on the platform
    """
    host = "www.ieeg.org"
    port = ""
    method = 'https://'

    def __init__(self, name, pwd, verify_ssl=True, mprov_listener=None):
        self.username = name
        use_https = Session.method.startswith('https')
        # Session.url_builder requires Session.port == ':8080' to use port 8080.
        # But there shouldn't be anyone calling url_builder anyway.
        port = Session.port[1:] if Session.port.startswith(
            ':') else Session.port
        self.api = IeegApi(self.username, pwd,
                           use_https=use_https, host=Session.host, port=port, verify_ssl=verify_ssl)
        self.mprov_listener = mprov_listener

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


    def close(self):
        self.api.close()

    @deprecated
    def url_builder(self, path):
        return Session.method + Session.host + Session.port + path

    def open_dataset(self, name):
        """
        Return a dataset object
        """

        get_id_response = self.api.get_dataset_id_by_name(name)

        # Check response
        if get_id_response.status_code != 200:
            print(get_id_response.text)
            raise IeegConnectionError('Authorization failed or cannot find study ' + name)

        snapshot_id = get_id_response.text

        time_series_details_response = self.api.get_time_series_details(snapshot_id)

        if time_series_details_response.status_code != 200:
            print(time_series_details_response.text)
            raise IeegConnectionError('Authorization failed or cannot get time series details for ' + name)

        # Return Habitat Dataset object
        return DS(ET.fromstring(time_series_details_response.text), snapshot_id, self)

    def close_dataset(self, ds):
        """
        Close connection (for future use)
        :param ds: Dataset to close
        :return:
        """
        return

    # For backward-compatibility
    @deprecated
    def urlBuilder(self, path):
        return self.url_builder(path)

    @deprecated
    def openDataset(self, name):
        return self.open_dataset(name)
