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

from ckanext.ngds.env import ckan_model
from ckan.plugins import toolkit
from ckan.logic import NotFound

def is_spatialized(resource):
    """
    Checks whether given resource is already spatialized. If spatialized returns True otherwise False.
    """
    spatialized = False
    resource_id = resource['id']
    package_id=ckan_model.Resource.get(resource_id).resource_group.package_id
    package = ckan_model.Package.get(package_id)
    for resource in package.resources:
        if 'protocol' in resource.extras and 'parent_resource' in resource.extras:
            extras = resource.extras
            try:
                toolkit.get_action('resource_show')(None, { 'id':resource.id,'for-view':True })
            except (NotFound):
                continue

            if extras['parent_resource'] == resource_id\
                and ( extras['protocol'].lower() == 'ogc:wms' or extras['ogc_type'].lower() == 'ogc:wfs'):
                print resource.state
                if resource.state !='active':
                    return False
                spatialized = True
                break
    return spatialized
