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

from osgeo import ogr
from osgeo import osr
import zipfile
from os import path
from re import search
from ckanext.ngds.ngdsui.misc.helpers import file_path_from_url
from pylons import config
from ckan.plugins import toolkit
import ckan.plugins as p

class Shapefile(object):
    resource = {}
    file_path = ""
    is_valid = False
    unzipped_dir = None
    ogr_source = {
        "driver": None,
        "source": None,
        "layer": None,
        "srs": None,
        "geom_extent": None
    }
    ogr_destination = {
        "driver": None,
        "source": None,
        "layer": None,
        "srs": None,
        "geom_extent": None
    }

    def __init__(self, resource_id=""):
        # Get the resource
        self.resource = toolkit.get_action("resource_show")(None, {"id": resource_id})
        
        # Get the path to the file
        url = self.resource["url"]
        self.file_path = file_path_from_url(url)
        
        # Check that it is a valid zip file
        self.is_valid = self.validate()

    def validate(self):
        """Make sure that the uploaded zip file is a valid shapefile"""        
        # Check that it is a zip file
        if zipfile.is_zipfile(self.file_path):
            # Open the zipfile as read-only
            with zipfile.ZipFile(self.file_path) as zf:
                required = [".shp", ".shx", ".dbf"]
                optional = [".prj", ".sbn", ".sbx", ".fbn", ".fbx", ".ain", ".aih", ".ixs", ".mxs", ".atx", ".cpg", ".xml"]
                
                # Look at the file extensions in the zipfile
                extensions = [path.splitext(info.filename)[1] for info in zf.infolist()]
                
                # Check that all the required extensions are there
                if len([ext for ext in required if ext in extensions]) == len(required):
                    # Check that there are not extension in there that are not required
                    if len([ext for ext in extensions if ext in optional]) == len(extensions) - len(required):
                        return True

        raise Exception(toolkit._("Not a valid shapefile"))

    def unzip(self):
        """Unzip the shapefile into a pre-determined directory next to it"""
        # Generate the path for the directory to be unzipped to
        unzipped_dir = self.file_path[:-4] + "_UNZIPPED"
        
        # Open the zipfile and extract everything (overwrite if there's stuff there??)
        with zipfile.ZipFile(self.file_path) as zf:
            zf.extractall(unzipped_dir)
        
        # Return the path to the unzipped directory
        return unzipped_dir
    
    def get_source_layer(self):
        """Get a OGRLayer for this shapefile"""

        # Where is the unzipped shapefile?
        if self.unzipped_dir is None:
            self.unzipped_dir = self.unzip()

        # Generate the OGR DataSource
        input_driver = ogr.GetDriverByName("ESRI Shapefile")
        input_datasource = input_driver.Open(self.unzipped_dir, 0)
        
        # A dataSource is always an array, but shapefiles are always by themselves. Get the layer
        layer = input_datasource.GetLayerByIndex(0)
        geom = layer.GetExtent()
        geom_extent = [[geom[2],geom[0]],[geom[3],geom[1]]]

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_source["driver"] = input_driver
        self.ogr_source["source"] = input_datasource
        self.ogr_source["layer"] = layer
        self.ogr_source["geom_extent"] = geom_extent

        return layer

    def ogr_source_info(self):
        source = self.ogr_source
        return source

    def get_destination_source(self):
        """Get an OGRDataSource for the default PostgreSQL destination"""
        # Generate connection details from CKAN config
        datastore_url = config.get("ckan.datastore.write_url")
        pattern = "://(?P<user>.+?):(?P<password>.+?)@(?P<host>.+?)/(?P<dbname>.+)$"
        params = search(pattern, datastore_url)
        connection = (
            params.group("host"),
            params.group("dbname"),
            params.group("user"),
            params.group("password")
        )
        ogr_connection_string = "PG: host=%s port=5432 dbname=%s user=%s password=%s" % connection
        
        # Generate the destination DataSource
        try:
            output_driver = ogr.GetDriverByName("PostgreSQL")
            destination_source = output_driver.Open(ogr_connection_string, True)

            # Cache the OGR objects so they don't get cleaned up
            self.ogr_destination["driver"] = output_driver
            self.ogr_destination["source"] = destination_source

            return destination_source
        except Exception as ex:
            return None

    def create_destination_layer(self, destination_source, name, epsg=4326):
        """Create a table in the given destination OGRDataSource"""
        # Get the shapefile OGR Layer and its "definition"
        source = self.get_source_layer()
        source_def = source.GetLayerDefn()
        
        # Read some shapefile properties
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_source["srs"] = srs

        # Multi any single geometry types
        geom_type = self.output_geom(source)

        # Create the destination layer in memory
        new_layer = destination_source.CreateLayer(name, srs, geom_type, ["OVERWRITE=YES"])
        
        # Iterate through shapefile fields, add them to the new layer
        for i in range(source_def.GetFieldCount()):
            field_def = source_def.GetFieldDefn(i)
            new_layer.CreateField(field_def)
        
        # Commit it
        new_layer.CommitTransaction()

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_destination["layer"] = new_layer

        return new_layer
        
    def get_destination_layer(self, destination_source=None, name=None):
        """Given an OGRDataSource (destination_source), find an OGRLayer within it by name"""
        if not destination_source:
            destination_source = self.get_destination_source()
        if not name:
            name = self.table_name()

        layer = destination_source.GetLayerByName(name)

        if not layer:
            layer = self.create_destination_layer(destination_source, name)

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_destination["layer"] = layer

        return layer
    
    def publish(self, destination_layer=None):
        """Move shapefile data into the given destination OGRLayer"""
        if not destination_layer:
            destination_layer = self.get_destination_layer()

        # Get information about the destination layer
        dest_def = destination_layer.GetLayerDefn()
        target_srs = destination_layer.GetSpatialRef()

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_destination["srs"] = target_srs
        
        # Setup the coordinate transformation
        source = self.get_source_layer()
        source_srs = source.GetSpatialRef()
        transformation = osr.CoordinateTransformation(source_srs, target_srs)

        # Remove any features currently in the destination layer -- they'll be replaced by shapefile contents
        dest_record = destination_layer.GetNextFeature()
        while dest_record is not None:
            destination_layer.DeleteFeature(dest_record.GetFID())
            dest_record = destination_layer.GetNextFeature()

        # Iterate through the shapefile features. Project each one and add it to the destination
        source_record = source.GetNextFeature()
        while source_record is not None:            
            # Create a new, blank feature in the destination layer
            dest_record = ogr.Feature(dest_def)
            
            # Set its geometry
            geom = source_record.GetGeometryRef()

            # Transform
            geom.Transform(transformation)

            # Force multi onto geoms
            geom_type = geom.GetGeometryType()
            force_function = self.output_geom_force(geom_type)
            geom = force_function(geom)

            # Set its attributes from the source feature
            dest_record.SetFrom(source_record)
            dest_record.SetGeometry(geom)
            
            # Save it to the destination layer and iterate
            destination_layer.CreateFeature(dest_record)
            source_record = source.GetNextFeature()

        return True

    def reproject(self, feature, target_srs):
        """Reproject a single feature's geometry into a new SRS and return the new geometry"""
        # Get the appropriate transformations and build a reprojected geometry
        source_srs = self.ogr_source["layer"].GetSpatialRef()
        transformation = osr.CoordinateTransformation(source_srs, target_srs)

        # Cache the OGR objects so they don't get cleaned up
        self.ogr_source["srs"] = source_srs
        self.transformation = transformation

        return feature.GetGeometryRef().Transform(transformation)

    def get_name(self):
        if self.unzipped_dir is None:
            self.unzipped_dir = self.unzip()

        # Generate the OGR DataSource
        inputDriver = ogr.GetDriverByName("ESRI Shapefile")
        dataSource = inputDriver.Open(self.unzipped_dir, 0)

        # A dataSource is always an array, but shapefiles are always by themselves. Get the layer
        return dataSource.GetLayerByIndex(0).GetName()

    def table_name(self):
        return self.get_name().lower().replace("-", "_") # Postgresql will have the name screwballed

    def output_geom(self, source):
        # Find the geometry type of the source shapefile
        source_def = source.GetLayerDefn()
        geom_type = source_def.GetGeomType()

        # Convert to Multi
        geom_type = ogr.wkbMultiLineString if geom_type == ogr.wkbLineString else geom_type
        geom_type = ogr.wkbMultiPolygon if geom_type == ogr.wkbPolygon else geom_type
        geom_type = ogr.wkbMultiPoint if geom_type == ogr.wkbPoint else geom_type

        return geom_type

    def output_geom_force(self, geom_type):
        # Return the correct function
        if geom_type == ogr.wkbLineString:
            return ogr.ForceToMultiLineString
        elif geom_type == ogr.wkbPolygon:
            return ogr.ForceToMultiPolygon
        elif geom_type == ogr.wkbPoint:
            return ogr.ForceToMultiPoint
        else:
            def do_nothing(geom):
                return geom
            return do_nothing
