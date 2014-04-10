import logging
import ckan.plugins as p
import ckan.plugins.toolkit as toolkit
from ckanext.geoserver.model import ProcessOGC as ogc
import ckan.logic as logic

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class OGCPreviewPlugin(p.SingletonPlugin):
    '''
    Custom class to add support to the Recline.js CKAN preview feature.
    '''

    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.IResourcePreview)

    OGC = ['wfs', 'wms', 'ogc:wfs', 'ogc:wms']

    # Add new resource containing libraries, scripts, etc. to the global config
    def update_config(self, config):
        toolkit.add_public_directory(config, 'theme/public')
        toolkit.add_template_directory(config, 'theme/templates')
        toolkit.add_resource('theme/public', 'geo-reclinepreview')

    # If the resource protocol is a WFS or WMS, then we can preview it
    def can_preview(self, data_dict):
        resource = data_dict['resource']
        format_lower = resource['format'].lower()
        if format_lower in self.OGC:
            return {'can_preview': True}
        else:
            return {'can_preview': False}

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
        error_log = data_dict['resource'].get("error", {})
        try:
            protocol = data_dict['resource'].get("protocol", {})
            if error_log is False and protocol == "OGC:WFS":
                return "wfs_preview_template.html"
            elif error_log is False and protocol == "OGC:WMS":
                return "wms_preview_template.html"
        except error_log is True:
            return "preview_error.html"