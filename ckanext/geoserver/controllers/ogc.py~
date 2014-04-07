from ckan.lib.base import *
from ckan.lib.navl.dictization_functions import DataError, unflatten, validate
from ckan.lib.base import (request,
                           render,
                           BaseController,
                           model,
                           abort, h, g, c)
from ckan.model.resource import Resource
import ckanext.ngds.geoserver.logic.action as action
from pylons import config
from pylons.decorators import jsonify
from ckan.logic import (tuplize_dict,clean_dict,
                        parse_params,flatten_to_string_key,get_action,check_access,NotAuthorized)
from ckan.controllers.storage import StorageController,StorageAPIController
import ckan.controllers.storage as storage
import json
import ckanext.ngds.contentmodel
import ckanext.ngds.contentmodel.shp2pg as shapefile
import sys

class OGCController(BaseController):

	@jsonify
	def publish_ogc(self):
		context = {'model': model, 'session': model.Session,'user': c.user or c.author}
		data = clean_dict(unflatten(tuplize_dict(parse_params(
            request.params))))	
		res = Resource().get(data['id'])
		url = res.url
		
		if url[len(url)-3:len(url)]=='zip':
			ofs = storage.get_ofs()
			BUCKET = config.get('ckan.storage.bucket', 'default')
			path_to_file = ofs.get_url(BUCKET,url.replace("%3A", ":").split("/storage/f/")[1])
			print path_to_file
	        shapefile.ZipfileHandler(path_to_file)

		if url[len(url)-3:len(url)]=='csv':
			action.datastore_spatialize(context,data)

		return {
			'success':True,
			'url':url
		}
