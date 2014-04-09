from ckanext.ngds.env import ckan_model
from ckan.plugins import toolkit
from ckan.logic import NotFound

def check_published(resource):
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
