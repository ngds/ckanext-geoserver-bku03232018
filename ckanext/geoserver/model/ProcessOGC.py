from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService
from osgeo import ogr

class HandleWMS():
    """
    Processor for WMS resources.  Requires a getCapabilities URL for the WMS and a WMS version passed in as a string.
    For now, only WMS v1.1.1 is supported by OWSLib.
    """

    def __init__(self, url, version="1.1.1"):
        self.wms = WebMapService(url, version=version)
        self.type = self.wms.identification.type
        self.version = self.wms.identification.version
        self.title = self.wms.identification.title
        self.abstract = self.wms.identification.abstract
        self.size = (256, 256)

    # Return a specific service URL, getMap is default
    def get_service_url(self, method='Get'):
        return self.wms.getOperationByName('GetMap').methods[method]['url']

    # Return an image format, *.png is default
    def get_format_options(self, format='image/png'):
        formats = self.wms.getOperationByName('GetMap').formatOptions
        if format in formats:
            return format
        else:
            return formats

    # Return a spatial reference system, default is WGS84
    def get_srs(self, layer, srs='EPSG:4326'):
        this_layer = self.wms[layer]
        srs_list = this_layer.crsOptions
        if srs in srs_list:
            return srs
        else:
            return "SRS Not Found"

    # Return bounding box of the service
    def get_bbox(self, layer):
        this_layer = self.wms[layer]
        return this_layer.boundingBoxWGS84

    # Pass in a dictionary with the layer name bound to 'layer'.  If the 'layer' is not found, then just return the
    # first layer in the list of available layers
    def do_layer_check(self, data_dict):
        layer_list = list(self.wms.contents)
        resource = data_dict.get("resource", {})
        this_layer = resource.get("layer")
        try:
            first_layer = layer_list[0]
            if this_layer in layer_list:
                return this_layer
            elif this_layer.lower() in layer_list:
                return this_layer.lower()
            else:
                return first_layer
        except Exception:
            pass

    # Return all of the information we need to access features in a WMS as one dictionary
    def get_layer_info(self, data_dict):
        layer = self.do_layer_check(data_dict)
        bbox = self.get_bbox(layer)
        srs = self.get_srs(layer)
        format = self.get_format_options()
        service_url = self.get_service_url()
        return {
            'layer': layer,
            'bbox': bbox,
            'srs': srs,
            'format': format,
            'service_url': service_url
        }

class HandleWFS():
    """
    Processor for WFS resources.  Requires a getCapabilities URL for the WFS and a WFS version passed in as a string.
    Default version is '1.0.0'; other supported versions are '1.1.0' and '2.0.0'
    """

    def __init__(self, url, version="1.0.0"):
        self.wfs = WebFeatureService(url, version=version)
        self.type = self.wfs.identification.type
        self.version = self.wfs.identification.version
        self.title = self.wfs.identification.title
        self.abstract = self.wfs.identification.abstract

    # Return a specific service URL, getFeature is default
    def get_service_url(self, operation='{http://www.opengis.net/wfs}GetFeature',
                        method='{http://www.opengis.net/wfs}Get'):
        return self.wfs.getOperationByName(operation).methods[method]['url']

    # Pass in a dictionary with the layer name bound to 'layer'.  If the 'layer' is not found, then just return the
    # first layer in the list of available layers
    def do_layer_check(self, data_dict):
        layer_list = list(self.wfs.contents)
        resource = data_dict.get("resource", {})
        this_layer = resource.get("layer")
        try:
            first_layer = layer_list[0]
            if this_layer in layer_list:
                return this_layer
            elif this_layer.lower() in layer_list:
                return this_layer.lower()
            else:
                return first_layer
        except Exception:
            pass

    # Build a URL for accessing service data, getFeature is default
    def build_url(self, typename=None, method='{http://www.opengis.net/wfs}Get',
                  operation='{http://www.opengis.net/wfs}GetFeature', maxFeatures=None):
        service_url = self.wfs.getOperationByName(operation).methods[method]['url']
        request = {'service': 'WFS', 'version': self.version}
        try:
            assert len(typename) > 0
            request['typename'] = ','.join([typename])
        except Exception:
            request['typename'] = ','.join('ERROR_HERE')
            pass

        if maxFeatures: request['maxfeatures'] = str(maxFeatures)

        encoded_request = "&".join("%s=%s" % (key,value) for (key,value) in request.items())
        url = service_url + "&" + encoded_request
        return url

    # Take a data_dict, use information to build a getFeature URL and get features as GML.  Then take that GML response
    # and turn it into GeoJSON.
    def make_geojson(self, data_dict):
        geojson = []
        type_name = self.do_layer_check(data_dict)
        wfs_url = self.build_url(type_name, maxFeatures=100)
        source = ogr.Open(wfs_url)
        layer = source.GetLayerByIndex(0)
        for feature in layer:
            geojson.append(feature.ExportToJson(as_object=True))
        return geojson

    # Recline.js doesn't support the GeoJSON specification and instead just wants it's own flavor of spatial-json.  So,
    # give this method the same data_dict you would give the 'make_geojson' method and we'll take the GeoJSON and turn
    # it into Recline JSON.
    def make_recline_json(self, data_dict):
        recline_json = []
        geojson = self.make_geojson(data_dict)
        for i in geojson:
            properties = i['properties']
            properties.update(dict(geometry=i['geometry']))
            recline_json.append(properties)
        return recline_json