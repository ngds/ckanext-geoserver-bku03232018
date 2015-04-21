'''import bin.datastore_setup as setup'''
import logging
import json
import ckan.lib.cli as cli
from ckan.lib.base import (model, c)
from ckan.plugins import toolkit

import pprint
pp = pprint.PrettyPrinter(indent=4)

log = logging.getLogger(__name__)


class SetupDatastoreCommand(cli.CkanCommand):
    '''Perform commands to set up the datastore.
    Make sure that the datastore urls are set properly before you run these commands.

    Usage::

        paster datastore set-permissions SQL_SUPER_USER

    Where:
        SQL_SUPER_USER is the name of a postgres user with sufficient
                         permissions to create new tables, users, and grant
                         and revoke new permissions.  Typically, this would
                         be the "postgres" user.


    Usage::

        paster geoserver publish-ogc PACKAGE_ID

    Where:
        PACKAGE_ID is the ID of the dataset that needs to be published to OGC

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    def __init__(self, name):

        super(SetupDatastoreCommand, self).__init__(name)

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print SetupDatastoreCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()


        if cmd == 'set-permissions':
            '''
            self.db_write_url_parts = cli.parse_db_config('ckan.datastore.write_url')
            self.db_read_url_parts = cli.parse_db_config('ckan.datastore.read_url')
            self.db_ckan_url_parts = cli.parse_db_config('sqlalchemy.url')

            assert self.db_write_url_parts['db_name'] == self.db_read_url_parts['db_name'],\
                "write and read db have to be the same"

            if len(self.args) != 2:
                print self.usage
                return

            setup.set_permissions(
                pguser=self.args[1],
                ckandb=self.db_ckan_url_parts['db_name'],
                datastoredb=self.db_write_url_parts['db_name'],
                ckanuser=self.db_ckan_url_parts['db_user'],
                writeuser=self.db_write_url_parts['db_user'],
                readonlyuser=self.db_read_url_parts['db_user']
            )
            if self.verbose:
                print 'Set permissions for read-only user: SUCCESS'
            '''
        elif cmd == 'publish-ogc':
            if len(self.args) != 2:
                print self.usage
                return

            package_id = self.args[1]

            self.publish_ogc(package_id)
        else:
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return

    def publish_ogc(self, package_id):
        '''
        Publish dataset wms/wfs resources to geoserver
        ''' 

	result = {
            'success': False,
            'message': toolkit._("Not enough information to publish this resource.")
        }


        # set other api call  
    	username    = 'admin'#context.get("user", None)
    	lat_field   = 'LatDegree'
    	lng_field   = 'LongDegree' 
	state       = 'AL' 


        # get usgin csv resouce id
        pkg         = toolkit.get_action('package_show')(None, {'id': package_id})
	resources   = pkg.get('resources', [])

        for resource in resources:
            if resource['format'].lower() == 'csv':
                resource_id = resource['id']
                layer_name  = resource['layer_name']
                break

	# get layer from package
	try:
	    md_package = None
	    extras     = pkg.get('extras', [])

            for extra in extras:
                key = extra.get('key', None)
                if key == 'md_package':
                    md_package = json.loads(extra.get('value'))
                    break
                
	    resourceDescription = md_package.get('resourceDescription', {})
	    layer               = resourceDescription.get('usginContentModelLayer', resource_id)
	    version             = resourceDescription.get('usginContentModelVersion', None)

	except:
	    return result


	workspace_name = state + '' + layer_name
        pp.pprint('DEBUG#20')
        pp.pprint(package_id)
        pp.pprint(resource_id)
        pp.pprint(workspace_name)
        pp.pprint(layer_name)
        pp.pprint(username)
        pp.pprint(lat_field)
        pp.pprint(lng_field)
        pp.pprint(version)

	try:
	    result = toolkit.get_action('geoserver_publish_ogc')(context, {
                'package_id'     : package_id, 
                'resource_id'    : resource_id, 
                'workspace_name' : workspace_name, 
                'layer_name'     : layer_name, 
                'username'       : username, 
                'col_latitude'   : lat_field, 
                'col_longitude'  : lng_field, 
                'layer_version'  : version})
	except:
            pp.pprint('DEBUG-FAIL')
	    return {
                'success': False,
                'message': toolkit._("An error occured while processing your request, please contact your administrator.")
            }

	return result


