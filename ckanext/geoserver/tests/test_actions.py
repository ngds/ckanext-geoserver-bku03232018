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
from sqlalchemy import create_engine, MetaData, Table, Column, Integer
from ckanext.ngds.geoserver.logic.action import publish
from ckanext.ngds.geoserver.model.Geoserver import Geoserver
from ckan.controllers import storage
from geoserver.layer import Layer as GeoserverLayer
from pylons import config
from datetime import datetime
import os

shapefile_name = "test_shapefile_wgs84.zip"
test_shapefile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "test-shapefile", shapefile_name))


class ActionsTestCase(NgdsTestCase):
    #csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "simple-csv.csv"))
    datastore_url = config.get("ckan.datastore.write_url")

    def createTable(self, resource_id):
        """Create a table in the Datastore database. This simulates having uploaded a csv and it being Datastorered"""
        engine = create_engine(self.datastore_url)
        metadata = MetaData()
        test_table = Table(
            resource_id,
            metadata,
            Column("id", Integer, primary_key=True),
            Column("lat", Integer),
            Column("lng", Integer)
        )
        test_table.create(bind=engine, checkfirst=True)

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

    def test_publish_csv(self):
        """Check that CSV publishing works like it should"""
        # Create a package
        p = self.add_package("test_publish_csv")

        # Create a resource
        p = self.add_resource(p["id"], {"package_id": p["id"], "url": "http://nothing.com/false.csv"})

        # Do the Datastorer part
        resource_id = p.get("resources")[0]["id"]
        self.createTable(resource_id)

        # Assemble params for the publish function
        context = {"user": self.admin_user().name}
        params = {
            "package_id": p["id"],
            "resource_id": resource_id,
            "layer_name": "test-csv-publish-layer",
            "col_latitude": "lat",
            "col_longitude": "lng"
        }

        # Publish it via action
        response = publish(context, params)

        # Assertions
        gs = Geoserver.from_ckan_config()
        self.assertIsInstance(gs.get_layer("test-csv-publish-layer"), GeoserverLayer)

    def test_publish_shapefile(self):
        """Check that Shapefile publishing works like it should"""
        # Create a package and resource
        package_name = "test_publish_shapefile"
        res = self.add_shapefile_resource(package_name)

        # Assemble params
        context = {"user": self.admin_user().name}
        params = {
            "package_id": package_name,
            "resource_id": res["id"],
            "layer_name": "test-shapefile-publish-layer",
        }

        # Publish it via action
        response = publish(context, params)

        # Assertions
        gs = Geoserver.from_ckan_config()
        self.assertIsInstance(gs.get_layer("test-shapefile-publish-layer"), GeoserverLayer)



