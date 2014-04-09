import logging
import ckan.plugins as plugin
from ckanext.ngds.geoserver.model import OGCServices as ogc
from ckan.plugins import IResourcePreview
import ckan.logic as logic

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust

class OGCPreviewPlugin(plugin.SingletonPlugin):
    '''
    Take the ogc recline previewer code and make it a separate plugin.
    '''

    plugin.implements(plugin.IConfigurer, inherit=True)
    plugin.implements(IResourcePreview)

    # Add new resource containing libraries, scripts, etc. to the global config
    def update_config(self, config):
        plugin.toolkit.add_template_directory(config, 'geo-recline/theme/templates')
        plugin.toolkit.add_resource('geo-recline/theme/public', 'geo-reclinepreview')

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
                this_resource = plugin.toolkit.c.resource
                this_resource["layer"] = ottoman["layer"]
                this_resource["bbox"] = ottoman["bbox"]
                this_resource["srs"] = ottoman["srs"]
                this_resource["format"] = ottoman["format"]
                this_resource["service_url"] = ottoman["service_url"]
                this_resource["error"] = False
            elif resource.get("protocol", {}) == "OGC:WFS":
                resourceURL = resource.get("url", {})
                armchair = ogc.HandleWFS(resourceURL)
                reclineJSON = armchair.make_recline_json(data_dict)
                this_resource = plugin.toolkit.c.resource
                this_resource["reclineJSON"] = reclineJSON
                this_resource["error"] = False
        except:
            plugin.toolkit.c.resource["error"] = True

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