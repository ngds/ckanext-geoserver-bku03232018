import logging

import ckanext.geoserver.logic.action as action
import ckanext.datastore.logic.auth as auth
import ckan.logic as logic
import ckanext.geoserver.misc.helpers as helpers

from ckanext.geoserver.common import plugins as p

from ckanext.geoserver.model.Geoserver import Geoserver

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class GeoserverPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('fanstatic', 'geoserver')

    # Functionality that this plugin provides through the Action API
    def get_actions(self):

        return {
            'geoserver_publish_ogc': action.publish_layer,
            'geoserver_unpublish_ogc': action.unpublish_layer,
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