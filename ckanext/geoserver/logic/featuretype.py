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

from collections import OrderedDict
import json
import ckanext.datastore.db as db
from geoserver.catalog import Layer
import ckanext.datastore.db as db
import sqlalchemy

class SqlFeatureTypeDef:

    def __init__(self, context, data_dict):
        
        baseGeoserverUrl = data_dict['geoserver']
        resource_id = data_dict['resource_id']
        layer_name = data_dict['layer_name']
        workspace_name = data_dict['workspace_name']
        
        if baseGeoserverUrl is None:
            print "using default geoserver :"+baseGeoserverUrl
            baseGeoserverUrl = 'http://localhost:8080/geoserver/rest/'
        
        # gets the fields of the resource_id in the database URl defined in
        # the context['connection']
        print ">>>>>>>>>>>>> reading field list >>>>>>>>>>>>>>>>>"
        fields = db._get_fields(context, data_dict)   
        print ">>>>>>>>>>>>> done reading field list >>>>>>>>>>>>>>>>>"
         
        self.name = layer_name
        self.title = layer_name
        
        # adds ""s in the field names putting them in another list
        self.fieldNames = [ "\"%s\"" % fld for fld in fields if fld not in ["id", "owningmap"] ]
        #print "fieldNames = "+fieldNames
        
        
        print ">>>>>>>>>>>>> building namespace >>>>>>>>>>>>>>>>>"
        self.namespace = {
            "name": workspace_name,
            "href": baseGeoserverUrl + "/namespaces/" + workspace_name + ".json"                  
        }
        
        
        #self.nativeCRS = layer.srs.wkt
        self.nativeCRS = 'EPSG:4326'
        
        print ">>>>>>>>>>>>> setting bounding box >>>>>>>>>>>>>>>>>"
     
        self.nativeBoundingBox = self.calcualte_bounding_box(context, data_dict)
        self.latLonBoundingBox = self.nativeBoundingBox
        print ">>>>>>>>>>>>>>>>> bounding box >>>>>>>>>>>>>>>>>>"
        print self.nativeBoundingBox
        
        
        
        print ">>>>>>>>>>>>> building geometry >>>>>>>>>>>>>>>>>"
        self.geometry = OrderedDict()
        self.geometry["name"] = data_dict['col_geography']
        self.geometry["type"] = 'shape'
        self.geometry["srid"] = 'EPSG:4326'
        
        print ">>>>>>>>>>>>> building virtual table >>>>>>>>>>>>>>>>>"
        self.virtualTable = OrderedDict()
        self.virtualTable["name"] = self.name
        self.virtualTable["sql"] = "select " + ", ".join(self.fieldNames) + " from \"" + resource_id+"\"" 
        self.virtualTable["geometry"] = self.geometry
        
        print ">>>>>>>>>>>>> building store >>>>>>>>>>>>>>>>>"
        self.store = {
            "@class": "dataStore",
            "name": "datastore",
            "href": baseGeoserverUrl + "/workspaces/" + workspace_name + "/datastores/datastore.json"              
        }
    
    def calcualte_bounding_box(self, context, data_dict):
        resource_id = data_dict['resource_id']
        col_latitude =  data_dict['col_longitude']
        col_longitude =  data_dict['col_latitude']

       
        query = sqlalchemy.text("SELECT MIN(\"" +col_latitude+"\"), MAX(\""+col_latitude+"\")"+
                ", MIN(\""+col_longitude+"\"), MAX(\""+col_longitude+"\")"+
                "FROM \""+resource_id+"\"")
        
        connection = context['connection']
        queryresult = connection.execute(query).fetchall()
        #queryresult = db._get_engine(None, data_dict).execute(query)
                
        result = {
            "minx": str(queryresult[0][0]),
            "maxx": str(queryresult[0][1]),
            "miny": str(queryresult[0][2]),
            "maxy": str(queryresult[0][3]),
            "crs": 'EPSG:4326'                          
        }
        
        
        return result
        
        
    def serialize(self):
        return json.dumps({
            "featureType": {
                "name": self.name,
                "title": self.title,
                "namespace": self.namespace,
                "nativeCRS": self.nativeCRS,
                "nativeBoundingBox": self.nativeBoundingBox,
                "latLonBoundingBox": self.latLonBoundingBox,
                "metadata": {
                    "entry": {
                        "@key": "JDBC_VIRTUAL_TABLE",
                        "virtualTable": self.virtualTable          
                    }             
                },
                "store": self.store                
            }              
        })
