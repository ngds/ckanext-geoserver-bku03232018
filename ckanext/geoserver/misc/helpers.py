import re
import urllib2
from ckan import model
from ckan.plugins import toolkit
from ckan.logic import NotFound
from ckan.controllers import storage
from pylons import config

def check_published(resource):
    """
    Checks whether given resource is already spatialized. If spatialized returns True otherwise False.
    """
    spatialized = False
    resource_id = resource['id']
    package_id = model.Resource.get(resource_id).resource_group.package_id
    package = model.Package.get(package_id)
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

def file_path_from_url(url):
    """
    Given a file's URL, find the file itself on this system
    """

    pattern = "^(?P<protocol>.+?)://(?P<host>.+?)/.+/(?P<label>\d{4}-.+)$"
    label = re.match(pattern, url).group("label")
    return get_url_for_file(urllib2.unquote(label))

def get_url_for_file(label):
    """
    Returns the URL for a file given it's label.
    """
    bucket = config.get('ckan.storage.bucket', 'default')
    ofs = storage.get_ofs()
    return ofs.get_url(bucket, label).replace("file://", "")