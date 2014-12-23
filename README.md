###Geoserver Extension for CKAN

custom configurations:

geoserver.rest_url = 'geoserver://admin:geoserver@localhost:8080/geoserver/rest'
geoserver.default_workspace = 'ckan'
geoserver.workspace_name = ckan
geoserver.workspace_uri = 'http://localhost:5000/ckan'

###If you're using reverse proxy (apache -> tomcat) to access geoserver (e.g: wms layer, creating new layers ...) add these lines

geoserver.use_proxy = True
geoserver.proxied_path = /geoserver

- Don't forget to add apache config to proxy the requested link (http://yourlocal/geoserver/ckan) to tomcat (http://yourlocal:TomcatPort/geoserver/ckan)


Also requires this to be set:

ckan.datastore.write_url = 'postgresql://ckanuser:pass@localhost/datastore'
