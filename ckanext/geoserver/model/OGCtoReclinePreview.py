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

from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from osgeo import ogr

class WMSDataServiceToReclineJS():

    def __init__(self, url, version="1.1.1"):
        self.wms = WebMapService(url, version=version)
        self.type = self.wms.identification.type
        self.version = self.wms.identification.version
        self.title = self.wms.identification.title
        self.abstract = self.wms.identification.abstract
        self.size = (256, 256)

    def get_layers(self):
        return list(self.wms.contents)

    def get_srs(self, layer, srs='EPSG:4326'):
        thisSRS = srs
        thisLayer = self.wms[layer]
        srsList = thisLayer.crsOptions
        if thisSRS in srsList:
            return thisSRS
        else:
            return thisSRS + " not found"

    def get_service_operations(self):
        thisWMS = self.wms.operations
        return [op.name for op in thisWMS]

    def get_service_methods(self):
        thisWMS = self.wms.getOperationByName('GetMap').methods
        return thisWMS

    def get_GET_url(self):
        methods = self.get_service_methods()
        return methods['Get']['url']

    def get_service_format_options(self, format='image/png'):
        thisFormat = format
        thisWMS = self.wms.getOperationByName('GetMap').formatOptions
        if thisFormat in thisWMS:
            return thisFormat
        else:
            return thisWMS

    def get_layer_details(self, layer):
        keys = ['layer', 'bbox', 'srs', 'format']
        thisLayer = self.wms[layer]
        bbox = thisLayer.boundingBoxWGS84
        thisSRS = self.get_srs(layer)
        return dict(zip(keys,[thisLayer,bbox,thisSRS,'none']))

    def get_service_url(self, layer):
        thisFormat = self.get_service_format_options(format)
        layer_details = self.get_layer_details(layer)
        serviceURL = self.wms.getmap(layers=[layer],
                                srs=layer_details['srs'],
                                bbox=layer_details['bbox'],
                                size=self.size,
                                format=thisFormat)
        return serviceURL

    def hack_up_a_layer_name(self, data_dict):
        data = data_dict.get("resource")
        if data.get("layer_name"):
            return data.get("layer_name")
        elif data.get("layer"):
            return data.get("layer")
        elif data.get("layers"):
            return data.get("layers")
        else:
            try:
                layer_list = self.get_layers()
                return layer_list[0]
            except:
                return "Sorry, can't find a layer!"

    def recline_ogc_wms(self, data_dict):
        data = data_dict
        keys = ["layer", "url"]
        layer = self.hack_up_a_layer_name(data)
        url = self.get_GET_url()
        return dict(zip(keys,[layer,url]))

    def ogc_wms_variables(self, data_dict):
        data

class WFSDataServiceToReclineJS():

    def __init__(self, url, version="1.0.0"):
        self.wfs = WebFeatureService(url, version=version)
        self.type = self.wfs.identification.type
        self.version = self.wfs.identification.version
        self.title = self.wfs.identification.title
        self.abstract = self.wfs.identification.abstract

    def get_layer_list(self):
        return list(self.wfs.contents)

    def get_single_layer(self, layer):
        theseLayers = self.get_layer_list()
        return [i for i in theseLayers if i == layer]

    def get_service_operations(self):
        thisWFS = self.wfs.operations
        return [op.name for op in thisWFS]

    def get_GET_feature_operation(self):
        operations = self.get_service_operations()
        return [i for i in operations if i.endswith("GetFeature")][0]

    def get_service_methods(self, service_operation):
        thisWFS = self.wfs
        thisOperation = service_operation
        return thisWFS.getOperationByName(thisOperation).methods
    #
    def get_service_method_URL(self, service_operation):
        thisWFS = self.wfs
        thisOperation = service_operation
        return thisWFS.getOperationByName('{http://www.opengis.net/wfs}GetFeature').methods['{http://www.opengis.net/wfs}Get']['url']

    def get_service_format_options(self, service_operation):
        thisWFS = self.wfs
        thisOperation = service_operation
        return thisWFS.getOperationByName(thisOperation).formatOptions

    def get_GML_format_option(self, service_operation):
        formatOptions = self.get_service_format_options(service_operation)
        return [i for i in formatOptions if i.endswith("GML2")][0]

    def get_response(self, layer):
        thisLayer = self.get_single_layer(layer)
        thisOperation = self.get_GET_feature_operation()
        thisGML = self.get_GML_format_option(thisOperation)
        response = self.wfs.getfeature(typename=thisLayer)
        return response

    def get_items(self):
        return self.wfs.items()

    def hack_up_a_layer_name(self, data_dict):
        data = data_dict.get("resource")
        if data.get("layer_name"):
            return data.get("layer_name")
        elif data.get("layer"):
            return data.get("layer")
        elif data.get("layers"):
            return data.get("layers")
        else:
            try:
                layer_list = self.get_layers()
                return layer_list[0]
            except:
                return "Sorry, can't find a layer!"

    def make_recline_url(self, data_dict):
        data = data_dict
        thisLayer = self.hack_up_a_layer_name(data).lower()
        getMethod = self.get_GET_feature_operation()
        baseURL = self.get_service_method_URL(getMethod)
        baseURL += "&service=WFS&version=1.0.0&typeName="
        baseURL += thisLayer
        return baseURL

    def MakeReclineJSON(self, data_dict):
        json_obj = []
        attribs = []
        data = data_dict
        gml_wfs = self.make_recline_url(data)
        source = ogr.Open(gml_wfs)
        print source
        layer = source.GetLayerByIndex(0)
        print layer

        for feature in layer:
            json_obj.append(feature.ExportToJson(as_object=True))

        for i in json_obj:
            properties = i['properties']
            properties.update(dict(geometry=i['geometry']))
            attribs.append(properties)

        return attribs
