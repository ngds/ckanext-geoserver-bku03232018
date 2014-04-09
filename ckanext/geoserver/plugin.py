import logging

import ckan.plugins as plugin
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

    plugin.implements(plugin.IActions)
    plugin.implements(plugin.IAuthFunctions)
    plugin.implements(ITemplateHelpers, inherit=True)

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

    def get_helpers(self):

        return {
            'geoserver_check_published': helpers.check_published,
        }