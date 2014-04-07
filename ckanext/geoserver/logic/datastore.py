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

import json

class PostGISDatastoreDef:
    def __init__(self, workspace):
        
        self.workspace = {
            "name": workspace.name,
            "href": workspace.href
        }
        
        # default values
        port = '5432'
        host = "localhost"
        password = 'geoserver'
        user = 'admin'
        database = 'datastore'
        
        
        self.connectionParameters = [
            ("Connection timeout", "20"),
            ("port", port),
            ("passwd", password),
            ("dbtype", "postgis"),
            ("host", host),
            ("validate connections", "false"),
            ("max connections", "10"),
            ("database", database),
            ("namespace", self.workspace["href"]),
            ("schema", "public"),
            ("Loose bbox", "true"),
            ("Expose primary keys", "false"),
            ("Max open prepared statements", "50"),
            ("preparedStatements", "false"),
            ("Estimated extends", "true"),
            ("user", user),
            ("min connections", "1"),
            ("fetch size", "1000"),                                         
        ]
        
    def serialize(self):
        return json.dumps({
            "dataStore": {
                "name": "django",
                "type": "PostGIS",
                "enabled": True,
                "workspace": self.workspace,
                "connectionParameters": {
                    "entry": [{"@key": key[0], "$": key[1]} for key in self.connectionParameters]                        
                },
                "__default": False
            }           
        })
