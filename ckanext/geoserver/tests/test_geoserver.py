""" NGDS_HEADER_BEGIN

National Geothermal Data System - NGDS
https://github.com/ngds

File: <filename>

Copyright (c) 2014, Siemens Corporate Technology and Arizona Geological Survey

Please refer the the README.txt file in the base directory of the NGDS project:
https://github.com/ngds/ckanext-ngds/blob/master/README.txt

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero
General Public License as published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.  https://github.com/ngds/ckanext-ngds
ngds/blob/master/LICENSE.md or
http://www.gnu.org/licenses/agpl.html

NGDS_HEADER_END """

from ckanext.ngds.tests.ngds_test_case import NgdsTestCase
from ckanext.ngds.geoserver.model.Geoserver import Geoserver

class TestGeoserverConnector(NgdsTestCase):
    """
    These tests assume that Geoserver is running either at the default location (localhost:8080/geoserver) or else
    at a location specified in your pylons .ini file
    """

    def setUp(self):
        self.gs = Geoserver.from_ckan_config()

    def test_get_default_workspace(self):
        """Geoserver must be able to create or return the default workspace"""
        ws = self.gs.default_workspace()
        self.assertEqual(ws.name, "ngds") # should read from config

    def test_get_default_datastore(self):
        """Geoserver must be able to create or return the default datastore"""
        ds = self.gs.default_datastore()
        self.assertIsNotNone(ds)
