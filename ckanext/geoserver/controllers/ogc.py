from ckan.lib.navl.dictization_functions import unflatten
from ckan.lib.base import (request, BaseController, model, c)
from ckan.model.resource import Resource
import ckanext.geoserver.logic.action as action
from pylons.decorators import jsonify
from ckan.logic import (tuplize_dict, clean_dict, parse_params)
#from ckanext.geoserver.model.Geoserver import Geoserver
from ckan.plugins import toolkit
from ckan.common import request, response
import json

class OgcController(BaseController):
    @jsonify
    def publishOGC(self):
	"""
	Publishes the resource content into Geoserver.
	"""

	if request.method != 'POST' or not request.is_xhr:
	    return {
                'success': False,
                'message': toolkit._("Bad request - JSON Error: No request body data")
            }

	context = {'model': model, 'session': model.Session,
		'user': c.user or c.author, 'auth_user_obj': c.userobj}

	data = clean_dict(unflatten(tuplize_dict(parse_params(request.params))))

	result = {'success': False,
                  'message': toolkit._("Not enough information to publish this resource.")
            }

	resource_id = data.get("resource_id", None)
    	username = context.get("user", None)
    	package_id = data.get("package_id", None)
    	lat_field = data.get("geoserver_lat_field", None)
    	lng_field = data.get("geoserver_lng_field", None)

	#get layer from package
	try:
	    md_package = None
	    pkg = toolkit.get_action('package_show')(context, {'id': package_id})

	    extras = pkg.get('extras', [])

            for extra in extras:
                key = extra.get('key', None)
                if key == 'md_package':
                    md_package = json.loads(extra.get('value'))
                    break
	    resourceDescription = md_package.get('resourceDescription', {})
	    layer = resourceDescription.get('usginContentModelLayer', resource_id)
	except:
	    return result

	layer_name = data.get("layer_name", layer)

	if None in [resource_id, layer_name, username, package_id]:
	    return result

	try:
	    result = toolkit.get_action('geoserver_publish_ogc')(context, {'package_id': package_id, 'resource_id': resource_id, 'layer_name': layer_name, 'username': username, 'col_latitude': lat_field, 'col_longitude': lng_field})
	except:
	    return {
                'success': False,
                'message': toolkit._("An error occured while processing your request, please contact your administrator.")
            }

	return result
