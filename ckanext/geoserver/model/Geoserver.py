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

from geoserver.catalog import Catalog
from pylons import config as ckan_config
import re

class Geoserver(Catalog):

    @classmethod
    def from_ckan_config(cls):
        """
        Setup the Geoserver Catalog from CKAN configuration

        @param cls: This class.
        @return: a Geoserver catalog
        """
        url = ckan_config.get("geoserver.rest_url", "http://localhost:8080/geoserver/rest")

        # Look for user information in the geoserver url
        userInfo = re.search("://(?P<auth>(?P<user>.+?):(?P<pass>.+?)@)?.+", url)
        user = userInfo.group("user") or "admin"
        pwd = userInfo.group("pass") or "geoserver"

        # Remove it from the connection URL if it was there
        url = url.replace(userInfo.group("auth") or "", "")
        if url:
            url = url.replace('geoserver://', 'http://')
        else:
            pass

        # Make the connection
        return cls(url, username=user, password=pwd)

    def default_workspace(self):
        """
        Get a default workspace -- create if it does not exist

        @return: workspace instance
        """

        name = ckan_config.get("geoserver.workspace_name", "ngds")
        uri = ckan_config.get("geoserver.workspace_uri", "http://localhost:5000/ngds")

        ngds_workspace = self.get_workspace(name)
        if ngds_workspace is None:
            ngds_workspace = self.create_workspace(name, uri)
        return ngds_workspace

    def default_datastore(self):
        """
        Get default datastore, create if it does not exist

        @return: datastore instance
        """

        # Extract values from development.ini file
        datastore_url = ckan_config.get('ckan.datastore.write_url','postgresql://ckanuser:pass@localhost/datastore')

        # Extract connection details
        pattern = "://(?P<user>.+?):(?P<pass>.+?)@(?P<host>.+?)/(?P<database>.+)$"
        details = re.search(pattern, datastore_url)

        # Check if the default datastore exists
        store_name = details.group("database")
        default_ws = self.default_workspace()
        try:
            ds = self.get_store(store_name, default_ws)
        except Exception as ex:
            # Doesn't exist. Create it and update the connection parameters
            ds = self.create_datastore(store_name, default_ws)
            ds.connection_parameters.update(
                host=details.group("host"),
                port="5432",
                database=details.group("database"),
                user=details.group("user"),
                passwd=details.group("pass"),
                dbtype="postgis"
            )
            self.save(ds)

        # Return it
        return ds

    def get_datastore(self, name, store_name=None):
        datastore_url = ckan_config.get('ckan.datastore.write_url','postgresql://ckanuser:pass@localhost/datastore')
        pattern = "://(?P<user>.+?):(?P<pass>.+?)@(?P<host>.+?)/(?P<database>.+)$"
        details = re.search(pattern, datastore_url)
        workspace = self.get_workspace(name)
        if store_name is None:
            store_name = details.group("database")
        try:
            ds = self.get_store(store_name, workspace)
        except Exception as ex:
            ds = self.create_datastore(store_name, workspace)
            ds.connection_parameters.update(
                host=details.group("host"),
                port="5432",
                database=details.group("database"),
                user=details.group("user"),
                passwd=details.group("pass"),
                dbtype="postgis"
            )
            self.save(ds)
        return ds
