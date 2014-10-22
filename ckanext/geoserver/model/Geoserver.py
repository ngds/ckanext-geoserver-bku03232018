from geoserver.catalog import Catalog
from pylons.config import config
import re

class Geoserver(Catalog):

    @classmethod
    def from_ckan_config(cls):
        """
        Setup the Geoserver Catalog from CKAN configuration

        @param cls: This class.
        @return: a Geoserver catalog
        """
        url = config.get("geoserver.rest_url", "http://localhost:8080/geoserver/rest")

        # Look for user information in the geoserver url
        userInfo = re.search("://(?P<auth>(?P<user>.+?):(?P<pass>.+?)@)?.+", url)
        user = userInfo.group("user") or "admin"
        pwd = userInfo.group("pass") or "geoserver"

        # Remove it from the connection URL if it was there
        url = url.replace(userInfo.group("auth") or "", "")
        if url:
            url = url.replace('geoserver://', 'http://')

        # Make the connection
        return cls(url, username=user, password=pwd)

    def default_workspace(self):
        """
        Get a default workspace -- create if it does not exist

        @return: workspace instance
        """

        name = config.get("geoserver.workspace_name", "ckan")
        uri = config.get("geoserver.workspace_uri", "http://localhost/ckan")

        ngds_workspace = self.get_workspace(name)
        if ngds_workspace is None:
            ngds_workspace = self.create_workspace(name, uri)
        return ngds_workspace

    def get_datastore(self, workspace=None, store_name=None):
        """
        Make a connection to the datastore, create the datastore if it does not exist.  The database we point to will
        be CKAN's datastore database in most cases because that's where all of our uploaded files wind up.  Otherwise,
        specify the name of the database you want to make a connection with through the 'store_name' argument.
        """

        # Extract values from ckan config file
        datastore_url = config.get('ckan.datastore.write_url','postgresql://ckanuser:pass@localhost/datastore')

        # Extract connection details
        pattern = "://(?P<user>.+?):(?P<pass>.+?)@(?P<host>.+?)/(?P<database>.+)$"
        details = re.search(pattern, datastore_url)

        # Give a name to the workspace and specify the datastore
        if workspace is None:
            workspace = self.default_workspace()
        if store_name is None:
            store_name = details.group("database")

        # Check if the datastore exists, create if it does not exist
        try:
            ds = self.get_store(store_name, workspace)
        except Exception as ex:
            ds = self.create_datastore(store_name, workspace)
            ds.connection_parameters.update(
                host=details.group("host"),
                port="5432",
                database=details.group("database"),
                user=details.group("user"),
                passwd=details.group("pass"),
                dbtype="postgis"
            )
            self.save(ds)

        # Return datastore object
        return ds
