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

from ckan.lib.navl.dictization_functions import unflatten
from ckan.lib.base import (request, BaseController, model, c)
from ckan.model.resource import Resource
import ckanext.ngds.geoserver.logic.action as action

from pylons.decorators import jsonify
from ckan.logic import (tuplize_dict, clean_dict, parse_params)

class OGCController(BaseController):

    @jsonify
    def publish_ogc(self):
        """
        Publishes the resource content into Geoserver. Shape file and csv files are handled differently.
        """
        context = {'model': model, 'session': model.Session, 'user': c.user or c.author}
        data = clean_dict(unflatten(tuplize_dict(parse_params(request.params))))
        res = Resource().get(data['id'])
        uri = Resource().get(data['id']).extras['content_model_version']
        url = res.url

        if url[len(url)-3:len(url)] == 'zip':
            action.shapefile_expose_as_layer(context, data)

        if url[len(url)-3:len(url)]=='csv':
            action.datastore_spatialize(context,data)

        return {
            'success':True,
            'url':url
        }
