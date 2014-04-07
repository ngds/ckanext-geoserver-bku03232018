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

import ckan.plugins as p
from ckan.plugins import ITemplateHelpers, IRoutes, IResourcePreview
import ckanext.ngds.geoserver.logic.action as action
from ckanext.ngds.geoserver.model import OGCServices as ogc
import ckanext.datastore.logic.auth as auth
import ckan.logic as logic
import ckanext.ngds.geoserver.misc.helpers as helpers

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class GeoserverPlugin(p.SingletonPlugin):
    '''
    Geoserver plugin.
    
    This plugin provides actions to "spatialize" tables in the datastore and to connect them with the Geoserver. Spatialize 
    means:
    1. Create an additional column of type (PostGIS) point
    2. Update the column with values calulated from already existing latitude/ longitude columns
    
    Connect to Geoserver means:
    1. Create a select statement
    2. Use the geoserver API to create a new layer using that select statement 
     
    '''
    # p.implements(p.IConfigurable, inherit=True)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

    def get_actions(self):

        actions = {
            'geoserver_publish_layer': action.publish,
            'geoserver_layer_exists': action.layer_exists,
            'geoserver_unpublish_layer': action.unpublish,
            'get_wms': action.map_search_wms,
        }

        return actions

    def get_auth_functions(self):
        functions = {'datastore_spatialize': auth.datastore_create,
                     'datastore_expose_as_layer': auth.datastore_create,
                     'datastore_is_spatialized': auth.datastore_search,
                     'datastore_is_exposed_as_layer': auth.datastore_search,
                     'datastore_remove_exposed_layer': auth.datastore_delete,
                     'datastore_remove_all_exposed_layers': auth.datastore_delete,
                     'datastore_list_exposed_layers': auth.datastore_search,
                     'geoserver_create_workspace': auth.datastore_create,
                     'geoserver_delete_workspace': auth.datastore_delete,
                     'geoserver_create_store': auth.datastore_create,
                     'geoserver_delete_store': auth.datastore_delete}

        return functions

    p.implements(ITemplateHelpers, inherit=True)

    def get_helpers(self):
        return {
            'is_spatialized': helpers.is_spatialized,
        }

    p.implements(IRoutes, inherit=True)

    def before_map(self, map):
        map.connect('spatialize', '/ngds/publish_ogc',
                    controller="ckanext.ngds.geoserver.controllers.ogc:OGCController", action="publish_ogc",
                    conditions={"method": ["POST"]})
        map.connect('publish_layer', '/ngds/publish_layer',
                    controller="ckanext.ngds.geoserver.controllers.ogc:OGCController", action="publish_layer",
                    conditions={"method": ["POST"]})

        return map

    # Start WFS preview plugin

    p.implements(p.IConfigurer, inherit=True)

    # Add new resource containing libraries, scripts, etc. to the global config
    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'geo-recline/theme/templates')
        p.toolkit.add_resource('geo-recline/theme/public', 'geo-reclinepreview')

    p.implements(IResourcePreview)

    # If the resource protocol is a WFS, then we can preview it
    def can_preview(self, data_dict):
        if data_dict.get("resource", {}).get("protocol", {}) == "OGC:WFS":
            return True
        elif data_dict.get("resource", {}).get("protocol", {}) == "OGC:WMS":
            return True

    # Get the GML service for our resource and parse it into a JSON object
    # that is compatible with recline.  Bind that JSON object to the
    # CKAN resource in order to pass it client-side.
    def setup_template_variables(self, context, data_dict):
        try:
            resource = data_dict.get("resource", {})
            if resource.get("protocol", {}) == "OGC:WMS":
                resourceURL = resource.get("url", {})
                armchair = ogc.HandleWMS(resourceURL)
                ottoman = armchair.get_layer_info(resource)
                p.toolkit.c.resource["layer"] = ottoman["layer"]
                p.toolkit.c.resource["bbox"] = ottoman["bbox"]
                p.toolkit.c.resource["srs"] = ottoman["srs"]
                p.toolkit.c.resource["format"] = ottoman["format"]
                p.toolkit.c.resource["service_url"] = ottoman["service_url"]
                p.toolkit.c.resource["error"] = False
            elif resource.get("protocol", {}) == "OGC:WFS":
                resourceURL = resource.get("url", {})
                armchair = ogc.HandleWFS(resourceURL)
                reclineJSON = armchair.make_recline_json(data_dict)
                p.toolkit.c.resource["reclineJSON"] = reclineJSON
                p.toolkit.c.resource["error"] = False
        except:
            p.toolkit.c.resource["error"] = True

    # Render the jinja2 template which builds the recline preview
    def preview_template(self, context, data_dict):
        error_log = data_dict.get("resource", {}).get("error", {})
        log.debug(error_log)
        try:
            protocol = data_dict.get("resource", {}).get("protocol", {})
            if error_log is False and protocol == "OGC:WFS":
                return "wfs_preview_template.html"
            elif error_log is False and protocol == "OGC:WMS":
                return "wms_preview_template.html"
        except error_log is True:
            log.debug('ERROR LOG IS TRUE')
            return "preview_error.html"
        else:
            return "preview_error.html"