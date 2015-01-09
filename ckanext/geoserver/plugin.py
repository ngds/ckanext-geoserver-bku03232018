import logging

import ckanext.geoserver.logic.action as action
import ckanext.datastore.logic.auth as auth
import ckan.logic as logic
import ckanext.geoserver.misc.helpers as helpers

from ckanext.geoserver.common import plugins as p

import logic.converters as converters

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class GeoserverPlugin(p.SingletonPlugin):

    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.ITemplateHelpers, inherit=True)
    p.implements(p.IDatasetForm)
    p.implements(p.IRoutes, inherit=True)

    def update_config(self, config):
        p.toolkit.add_template_directory(config, 'templates')
        p.toolkit.add_resource('fanstatic', 'geoserver')

    # IRoutes
    def before_map(self, map):
        controller = 'ckanext.geoserver.controllers.ogc:OgcController'
        map.connect('geoserver_publish_ogc', '/geoserver/publish-ogc', controller=controller, action='publishOGC')

	map.connect('geoserver_ogc_get_capabilities', '/geoserver/get-capabilities-ogc', controller=controller, action='getCapabilitiesOGC')

	return map


    # Functionality that this plugin provides through the Action API
    def get_actions(self):

        return {
            'geoserver_publish_ogc': action.publish_ogc,
            'geoserver_unpublish_ogc': action.unpublish_ogc,
            'geoserver_get_wms': action.map_search_wms,
        }

    def _modify_package_schema(self, schema):
        schema['resources'].update({
            'md_resource': [p.toolkit.get_validator('ignore_missing'),
                            converters.convert_to_geoserver_extras]
        })

    def create_package_schema(self):
        schema = super(GeoserverPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(GeoserverPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def is_fallback(self):
        return False

    def package_types(self):
        return []

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
