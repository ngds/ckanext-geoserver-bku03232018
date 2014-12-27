import logging
import ckan.logic as logic
from ckanext.geoserver.model.Geoserver import Geoserver
from ckanext.geoserver.model.Layer import Layer
from ckanext.geoserver.model.ProcessOGC import HandleWMS
from ckan.plugins import toolkit
from pylons.i18n import _
import ckan.lib.helpers as h
from ckan import model
import socket

log = logging.getLogger(__name__)
_get_or_bust = logic.get_or_bust


def publish_ogc(context, data_dict):
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
    datastore = data_dict.get("geoserver_datastore", None)
    layer_version = data_dict.get("layer_version", None)

    # Check that you have everything you need
    if None in [resource_id, layer_name, username, package_id, layer_version]:
        raise Exception(toolkit._("Not enough information to publish resource"))

    # Publish a layer
    def pub():
        layer = Layer.publish(package_id, resource_id, layer_name, layer_version, username, datastore, lat_field=lat_field,
                              lng_field=lng_field)
        return layer

    try:
        l = pub()
        if l is None:
	    log.debug("Failed to generate a Geoserver layer.")
            h.flash_error(_("Failed to generate a Geoserver layer."))
            raise Exception(toolkit._("Layer generation failed"))
        else:
            # csv content should be spatialized or a shapefile uploaded, Geoserver updated, resources appended.
            #  l should be a Layer instance. Return whatever you wish to
            h.flash_success(_("This resource has successfully been published as an OGC service."))
	    log.debug("This resource has successfully been published as an OGC service.")
            return {"success": True,
		    "message": _("This resource has successfully been published as an OGC service.")
		}
    except socket.error:
        h.flash_error(_("Error connecting to Geoserver."))
	log.debug("Error connecting to Geoserver.")


        # Confirm that everything went according to plan


def unpublish_ogc(context, data_dict):
    """
    Un-publishes the Geoserver layer based on the resource identifier. Retrieves the Geoserver layer name and package
     identifier to construct layer and remove it.
    """
    resource_id = data_dict.get("resource_id")
    layer_name = data_dict.get("layer_name")
    layer_name = "NGDS:" + resource_id
    username = context.get('user')
    file_resource = toolkit.get_action("resource_show")(None, {"id": resource_id})

    geoserver = Geoserver.from_ckan_config()

    package_id = model.Resource.get(resource_id).resource_group.package_id

    def unpub():
        layer = Layer(geoserver=geoserver, layer_name=layer_name, resource_id=resource_id, package_id=package_id,
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
