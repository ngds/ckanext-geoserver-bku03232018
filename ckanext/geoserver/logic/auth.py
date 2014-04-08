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

import ckan.plugins as p


def _datastore_auth(context, data_dict):
    if not 'id' in data_dict:
        data_dict['id'] = data_dict.get('resource_id')
    user = context.get('user')

    authorized = p.toolkit.check_access('resource_update', context, data_dict)

    if not authorized:
        return {
            'success': False,
            'msg': p.toolkit._('User {0} not authorized to update resource {1}'\
                    .format(str(user), data_dict['id']))
        }
    else:
        return {'success': True}

def datastore_create(context, data_dict):
    return _datastore_auth(context, data_dict)

def datastore_upsert(context, data_dict):
    return _datastore_auth(context, data_dict)

def datastore_delete(context, data_dict):
    return _datastore_auth(context, data_dict)

def datastore_search(context, data_dict):
    return _datastore_auth(context, data_dict)
