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

import bin.datastore_setup as setup
import logging

import ckan.lib.cli as cli

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

        self.db_write_url_parts = cli.parse_db_config('ckan.datastore.write_url')
        self.db_read_url_parts = cli.parse_db_config('ckan.datastore.read_url')
        self.db_ckan_url_parts = cli.parse_db_config('sqlalchemy.url')

        assert self.db_write_url_parts['db_name'] == self.db_read_url_parts['db_name'],\
            "write and read db have to be the same"

        if len(self.args) != 2:
            print self.usage
            return

        if cmd == 'set-permissions':
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
        else:
            print self.usage
            log.error('Command "%s" not recognized' % (cmd,))
            return
