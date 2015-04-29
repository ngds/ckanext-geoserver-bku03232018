'''import bin.datastore_setup as setup'''
import logging
import json
import pylons
import redis
import pprint
import sys
import usginmodels
import ckan.lib.cli as cli
from ckan.lib.base import (model, c, config)
from ckan.plugins import toolkit
from ckanext.metadata.logic import action as get_meta_action

HOSTNAME   = 'localhost'
REDIS_PORT = 6379
REDIS_DB   = 0


pp = pprint.PrettyPrinter(indent=4)

log = logging.getLogger(__name__)

class SetupDatastoreCommand(cli.CkanCommand):
    '''Perform commands to set up the datastore.
    Commands:
        paster geoserver publish-ogc PACKAGE_ID     - publishes dataset with PACKAGE_ID to geoserver
        paster geoserver publish-ogc-all            - publishes all datasets that follow the usgin model to geoserver
        paster geoserver publish-ogc-redis-queue    - creates a redis queue with datasets id that will be published to geoserver
        paster geoserver publish-ogc-worker         - start a worker process that polls the redis queue for new datasets 
                                                      and publishes them to the geoserver

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

        if cmd == 'publish-ogc':
            if len(self.args) != 2:
                print self.usage
                return

            package_id = u'' + self.args[1]

            self.publish_ogc(package_id)
        elif cmd == 'publish-ogc-all':
            self.publish_ogc_all()
        elif cmd == 'publish-ogc-worker':
            self.publish_ogc_worker()
        elif cmd == 'publish-ogc-redis-queue':
            self.publish_ogc_redis_queue()
        else:
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return


    def publish_ogc(self, package_id):
        '''
        Publish dataset wms/wfs resources to geoserver
        ''' 

        context = {
            'user': u'admin',
            'api_call_type' : u'paster',
        }

	result = {
            'success': False,
            'message': toolkit._("Not enough information to publish this resource.")
        }


        # set other api call parameters 
    	username    = context.get("user", None)
    	lat_field   = u'LatDegree'
    	lng_field   = u'LongDegree'

        # get usgin csv resouce id
        pkg         = toolkit.get_action('package_show')(context, {'id': package_id})
	resources   = pkg.get('resources', [])

        for resource in resources:
            if resource['format'].lower() == 'csv':
                resource_id = u'' + resource['id']
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

            # handle harvested datasets that do not have a md_package
            if layer == resource_id and version == None:
                usgin_tag = []

                for tag in pkg['tags']:
                    if tag['name'].startswith('usgincm:'):
                        usgin_tag.append(tag['name']) 

                for key,value in (get_meta_action.get_usgin_prefix()).iteritems():
                    if reduce(lambda v1,v2: v1 or v2, map(lambda v: v in usgin_tag, value)):
                        key_arr = key.split("+")
                        break

                layer   = key_arr[1]
                version = key_arr[2] 


	except:
	    return result

        layer_name     = layer
	workspace_name = u'' + package_id + '-' + layer_name

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

            #log.debug("Dataset: " + package_id + " has been successfully published to the GeoServer" )
            print "Dataset: " + package_id + " has been successfully published to the GeoServer"

	except:
	    error = {
                'success': False,
                'message': toolkit._("An error occured while processing your request, please contact your administrator.")
            }
            #log.debug("An error occured while processing your request, please contact your administrator.")
            print "An error occured while processing your request, please contact your administrator."

    
    def publish_ogc_all(self):
        '''
        Publish dataset wms/wfs resources to geoserver for all datasets
        that that have a valid usgin csv resource and. This command
        will not publish wmf/wfs resources to geoserver if a publishing 
        action has been performed before
        ''' 
        # get all usgin datasets that have not been published yet
        sql="""
        SELECT DISTINCT package.id AS package_id
        FROM package,
             package_extra,
             resource_group,
             resource,
             package_tag,
             tag
        WHERE package.id = package_extra.package_id
          AND package.state='active'
          AND resource_group.package_id=package.id
          AND resource_group.id = resource.resource_group_id
          AND package_tag.package_id = package.id
          AND tag.id = package_tag.tag_id
          AND tag.name LIKE '%usgincm:%'
        GROUP BY package.id
        HAVING COUNT(resource.id)=1;
        """
        rows = model.Session.execute(sql)

        for row in rows:
            self.publish_ogc(row.package_id)


    def publish_ogc_worker(self):
        '''
        Publish dataset wms/wfs to geoserver by pop-ing
        an element (dataset id) from the publis_ogc_queue(redis)
        ''' 
        r = self._redis_connection()

        # Lovely infinite loop ;P, we do need them from time to time
        while True:
            # POP an element (package_id) from publis_ogc_queue and publish it to ogc
            try:
                # we need to slow down this loop by setting the blpop timeout to 5 seconds
                # when publish_ogc_queue is empty
                queue_task = r.blpop('publish_ogc_queue', 5) 

                if queue_task is not None:
                    package_id = queue_task[1] 
                    self.publish_ogc(package_id)
                    log.debug('Dataset: ' + package_id + ' has been published to the GeoServer')

            except:
                log.debug('An Error has occured while publishing dataset:' + package_id + ' to GeoServer')


    def publish_ogc_redis_queue(self):
        '''
        Create the pubusish_ogc_queue by querying the db
        for datasets that require ogc publishing
        ''' 

        # todo: check config for backend redis/rabbitmq
        # get all usgin datasets that have not been published yet
        sql="""
        SELECT DISTINCT package.id AS package_id
        FROM package,
             resource_group,
             resource,
             package_tag,
             tag
        WHERE package.state='active'
          AND resource_group.package_id=package.id
          AND resource_group.id = resource.resource_group_id
          AND package_tag.package_id = package.id
          AND tag.id = package_tag.tag_id
          AND tag.name LIKE '%usgincm:%'
        GROUP BY package.id
        HAVING COUNT(resource.id)=1;
        """

        rows = model.Session.execute(sql)
        r    = self._redis_connection()

        # delete the queue before we add the fresh elements
        if r.exists('publish_ogc_queue'):
            r.delete('publish_ogc_queue')

        for row in rows:
            # push the dataset ids to the redis queue
            r.rpush('publish_ogc_queue', row.package_id)


    def _redis_connection(self):
        # redis connection
        try:
            r = redis.StrictRedis(
                host=config.get('ckan.harvest.mq.hostname', HOSTNAME),
                port=int(config.get('ckan.harvest.mq.port', REDIS_PORT)),
                db=int(config.get('ckan.harvest.mq.redis_db', REDIS_DB))
            )
            return r
        except:
            log.debug('Error Connecting to Redis while building publish_ogc_queue')
