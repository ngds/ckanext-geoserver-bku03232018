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

import ckan.plugins as plugins
from ckan.plugins import ITemplateHelpers, IRoutes
import ckanext.ngds.geoserver.logic.action as action
import ckanext.datastore.logic.auth as auth
import ckan.logic as logic
import ckanext.ngds.geoserver.misc.helpers as helpers

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class GeoserverPlugin(plugins.SingletonPlugin):
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

    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # Functionality that this plugin provides through the Action API
    def get_actions(self):

        return {
            'geoserver_publish_layer': action.publish_layer,
            'geoserver_unpublish_layer': action.unpublish_layer,
            'geoserver_get_wms': action.map_search_wms,
        }

    # Functionality for providing user authentication and authorization
    def get_auth_functions(self):

        return {
            'datastore_spatialize': auth.datastore_create,
            'datastore_expose_as_layer': auth.datastore_create,
            'datastore_is_spatialized': auth.datastore_search,
            'datastore_is_exposed_as_layer': auth.datastore_search,
            'datastore_remove_exposed_layer': auth.datastore_delete,
            'datastore_remove_all_exposed_layers': auth.datastore_delete,
            'datastore_list_exposed_layers': auth.datastore_search,
            'geoserver_create_workspace': auth.datastore_create,
            'geoserver_delete_workspace': auth.datastore_delete,
            'geoserver_create_store': auth.datastore_create,
            'geoserver_delete_store': auth.datastore_delete,
        }

    plugins.implements(ITemplateHelpers, inherit=True)

    def get_helpers(self):

        return {
            'geoserver_check_published': helpers.check_published,
        }