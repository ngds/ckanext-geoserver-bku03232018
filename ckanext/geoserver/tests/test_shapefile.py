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
from ckanext.ngds.geoserver.model.ShapeFile import Shapefile
from ckan.controllers import storage
from pylons import config
from datetime import datetime
from osgeo.ogr import DataSource, Layer

import os

#shapefile_name = "test_shapefile_wgs84.zip"
shapefile_name = "ca-active-faults.zip"
test_shapefile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test-shapefile", shapefile_name))


class ShapefileTestCase(NgdsTestCase):
    """
    These tests assume that Geoserver is running either at the default location (localhost:8080/geoserver) or else
    at a location specified in your pylons .ini file
    """

    def add_shapefile_resource(self, package_name, filepath=test_shapefile_path):
        # Add a package
        p = self.add_package(package_name)

        # "Upload" shapefile to the package
        ofs = storage.get_ofs()
        label = "%s/%s" % (datetime.now().isoformat(), shapefile_name)
        anything = ofs.put_stream(
            config.get('ckan.storage.bucket', 'default'), # bucket
            label, # label
            open(filepath, "r"), # file stream
            {"key": label} # params
        )

        # Add a resource
        package = self.add_resource(p["id"], {"package_id": p["id"], "url": "http://localhost:5000/storage/f/%s" % label})
        return package.get("resources", [None])[0]

    def setUp(self):
        pass

    def test_shapefile_path_exists(self):
        """Check that creating a shapefile instance finds the path to the compressed file"""
        shapefile_resource = self.add_shapefile_resource("test-path-exists")

        s = Shapefile(shapefile_resource["id"])
        self.assertTrue(os.path.exists(s.file_path))

    def test_shapefile_upload_garbage(self):
        """Garbage in raises an exception (garbage out)"""
        garbage_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test-shapefile", "test_shapefile.dbf"))
        garbage_resource = self.add_shapefile_resource("test-upload-garbage", garbage_path)
        self.assertRaises(Exception, Shapefile, garbage_resource["id"])

    def test_shapefile_dest_source(self):
        """Validate that we can open the datastore database as an OGRDataSource"""
        res = self.add_shapefile_resource("test-dest-source")
        s = Shapefile(res["id"])
        self.assertIsInstance(s.get_destination_source(), DataSource)

    def test_shapefile_dest_layer(self):
        """Check that we can create an OGRLayer in the datastore database"""
        res = self.add_shapefile_resource("test-create-dest-layer")
        s = Shapefile(res["id"])
        ds = s.get_destination_source()
        self.assertIsInstance(s.create_destination_layer(ds, "test-create-dest-layer"), Layer)

    def test_shapefile_dest_layer_fields(self):
        """The destination layer must contain the fields from the source"""
        res = self.add_shapefile_resource("test-dest-fields")
        s = Shapefile(res["id"])
        shapefile = s.get_source_layer().GetLayerDefn()
        source_fields = [shapefile.GetFieldDefn(i).GetName().lower() for i in range(shapefile.GetFieldCount())]

        dest = s.get_destination_layer(s.get_destination_source(), s.get_name()).GetLayerDefn()
        dest_fields = [dest.GetFieldDefn(i).GetName().lower() for i in range(dest.GetFieldCount())]

        self.assertEqual(len(set(source_fields).difference(dest_fields)), 0)

    def test_shapefile_get_dest_layer(self):
        """Check that we can get an OGRLayer in the datastore database"""
        res = self.add_shapefile_resource("test-get-dest-layer")
        s = Shapefile(res["id"])
        ds = s.get_destination_source()
        self.assertIsInstance(s.get_destination_layer(ds, s.table_name()), Layer)

    def test_shapefile_publish(self):
        """Publishing a shapefile puts the data into the PostGIS table"""
        res = self.add_shapefile_resource("test-publish")
        s = Shapefile(res["id"])
        self.assertTrue(s.publish())
        self.assertEqual(s.get_source_layer().GetFeatureCount(), s.get_destination_layer().GetFeatureCount())
