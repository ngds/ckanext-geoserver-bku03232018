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
from ckanext.ngds.geoserver.model.Layer import Layer
from ckanext.ngds.geoserver.model.Geoserver import Geoserver
from ckan.controllers import storage
from ckan.plugins import toolkit
from pylons import config
from datetime import datetime
from geoserver.layer import Layer as GeoserverLayer

import os

test_shapefile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test-shapefile", "test_shapefile_wgs84.zip"))


class LayerTestCase(NgdsTestCase):
    """
    These tests assume that Geoserver is running either at the default location (localhost:8080/geoserver) or else
    at a location specified in your pylons .ini file
    """
    _test_package_name = "default-for-geoserver-layer"
    _test_resource = None
    _test_package = None

    def setUp(self):
        try:
            self._test_package = toolkit.get_action("package_show")(
                {"user": self.admin_user().name},
                {"id": self._test_package_name}
            )
        except: pass

        if not self._test_package:
            # Add a package
            self._test_package = self.add_package(self._test_package_name)

            # "Upload" shapefile to the package
            ofs = storage.get_ofs()
            label = "%s/test_shapefile_wgs84.zip" % datetime.now().isoformat()
            anything = ofs.put_stream(
                config.get('ckan.storage.bucket', 'default'), # bucket
                label, # label
                open(test_shapefile_path, "r"), # file stream
                {"key": label} # params
            )
            # Add a resource
            self._test_package = self.add_resource(
                self._test_package["id"],
                {"package_id": self._test_package["id"], "url": "http://localhost:5000/storage/f/%s" % label}
            )

        self._test_resource = self._test_package.get("resources", [None])[0]

    def test_create_geo_resources(self):
        """Creating WFS/WMS resources should return two resources"""
        l = Layer(self._test_package["id"], self._test_resource["id"], "testing-layer", self.admin_user().name)
        self.assertEqual(len(l.create_geo_resources()), 2)

    def test_remove_geo_resources(self):
        """Removing resources should get rid of only the "geo" resources"""
        # Create a layer
        l = Layer(self._test_package["id"], self._test_resource["id"], "testing-layer", self.admin_user().name)

        # Add resources
        l.create_geo_resources()

        # Remove resources
        l.remove_geo_resources()

        # Check what's left
        p = toolkit.get_action("package_show")(None, {"id": self._test_package_name})
        self.assertEqual(len(p["resources"]), 1)

    def test_create_layer(self):
        """Check that a layer exists once create_layer is called"""
        # Create a layer
        l = Layer(self._test_package["id"], self._test_resource["id"], "testing-layer", self.admin_user().name)

        # Push to Geoserver
        self.assertIsInstance(l.create_layer(), GeoserverLayer)

        # Check that the layer exists
        gs = Geoserver.from_ckan_config()
        self.assertIsInstance(gs.get_layer("testing-layer"), GeoserverLayer)

    def test_remove_layer(self):
        """Check that a layer does not exist once remove_layer is called"""
        # Create a layer
        l = Layer(self._test_package["id"], self._test_resource["id"], "testing-layer", self.admin_user().name)

        # Push to Geoserver
        self.assertIsInstance(l.create_layer(), GeoserverLayer)

        # Remove the layer
        self.assertTrue(l.remove_layer())

        # Check that the layer no longer exists
        gs = Geoserver.from_ckan_config()
        self.assertIsNone(gs.get_layer("testing-layer"))

    def test_remove_layer_resource_check(self):
        """Check that the file resource no longer includes a "layer_name" once remove_layer is called"""
        # Create a layer
        l = Layer(self._test_package["id"], self._test_resource["id"], "testing-layer", self.admin_user().name)

        # Push to Geoserver
        self.assertIsInstance(l.create_layer(), GeoserverLayer)

        # Remove the layer
        self.assertTrue(l.remove_layer())

        # Check the resource
        resource = toolkit.get_action("resource_show")(
            {"user": self.admin_user().name},
            {"id": self._test_resource["id"]}
        )

        self.assertIsNone(resource.get("layer_name"))
