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

import logging
import ckan.logic as logic
from ckanext.ngds.geoserver.model.Geoserver import Geoserver
from ckanext.ngds.geoserver.model.Layer import Layer
from ckanext.ngds.geoserver.model.OGCServices import HandleWMS
from ckan.plugins import toolkit
from ckanext.ngds.env import ckan_model, h, _
import socket


log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust


def publish_layer(context, data_dict):
    """
    Publishes the resource details as a Geoserver layer based on the input details.
    If the layer creation is successful then returns "Success" msg, otherwise raises an Exception.
    """

    # Gather inputs
    resource_id = data_dict.get("resource_id", None)
    layer_name = data_dict.get("layer_name", resource_id)
    username = context.get("user", None)
    package_id = data_dict.get("package_id", None)
    lat_field = data_dict.get("col_latitude", None)
    lng_field = data_dict.get("col_longitude", None)
    geoserver_layer_name = data_dict.get("gs_lyr_name", None)
    datastore = data_dict.get("geoserver_datastore", None)

    # Check that you have everything you need
    if None in [resource_id, layer_name, username, package_id]:
        raise Exception(toolkit._("Not enough information to publish resource"))

    # Publish a layer
    def pub():
        if geoserver_layer_name is not None:
            l = Layer.publish(package_id, resource_id, geoserver_layer_name, username, datastore, lat_field=lat_field,
                              lng_field=lng_field)
            return l
        else:
            l = Layer.publish(package_id, resource_id, layer_name, username, datastore, lat_field=lat_field,
                              lng_field=lng_field)
            return l

    try:
        l = pub()
        if l is None:
            h.flash_error(
                _(
                    "Failed to generate a geoserver layer. Please contact the site administrator if this problem persists."))
            raise Exception(toolkit._("Layer generation failed"))
        else:
            # csv content should be spatialized or a shapefile uploaded, Geoserver updated, resources appended.
            #  l should be a Layer instance. Return whatever you wish to
            h.flash_success(
                _("This resource has successfully been published as an OGC service."))
            return "Success"
    except socket.error:
        h.flash_error(
            _("Error connecting to geoserver. Please contact the site administrator if this problem persists."))


        # Confirm that everything went according to plan


def unpublish(context, data_dict):
    """
    Un-publishes the Geoserver layer based on the resource identifier. Retrieves the Geoserver layer name and package
     identifier to construct layer and remove it.
    """
    resource_id = data_dict.get("resource_id")
    layer_name = data_dict.get("layer_name")
    layer_name = "NGDS:" + resource_id
    username = context.get('user')
    geoserver_layer_name = data_dict.get("gs_lyr_name", None)
    file_resource = toolkit.get_action("resource_show")(None, {"id": resource_id})

    if not layer_name:
        resource = ckan_model.Resource.get(resource_id)

    geoserver = Geoserver.from_ckan_config()

    package_id = ckan_model.Resource.get(resource_id).resource_group.package_id

    def unpub():
        if geoserver_layer_name is not None:
            layer = Layer(geoserver=geoserver, layer_name=geoserver_layer_name, resource_id=resource_id,
                          package_id=package_id, username=username)
            return layer
        else:
            layer = Layer(geoserver=geoserver, layer_name=layer_name, resource_id=resource_id,
                          package_id=package_id,
                          username=username)
            return layer

    try:
        layer = unpub()
    except socket.error:
        h.flash_error(
            _("Error connecting to geoserver. Please contact the site administrator if this problem persists."))
        return False

    layer.remove()
    h.flash_success(
        _("This resource has successfully been unpublished."))
    return True

def map_search_wms(context, data_dict):

    def wms_resource(resource):
        if resource.get("protocol", {}) == "OGC:WMS":
            return True
        else:
            return False

    def get_wms_data(resource):
        resourceURL = resource.get("url", {})
        this_wms = HandleWMS(resourceURL)
        return this_wms.get_layer_info(resource)
    try:
        pkg_id = data_dict.get("pkg_id")
        pkg = toolkit.get_action("package_show")(None, {'id': pkg_id})
        resources = filter(wms_resource, pkg.get('resources'))

        this_data = map(get_wms_data, resources)

        return this_data
    except:
        return [{'ERROR':'SERVER_ERROR'}]
