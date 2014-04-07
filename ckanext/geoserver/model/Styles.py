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
from Geoserver import Geoserver
from os import listdir, getcwd, makedirs, walk
from os.path import isfile, isdir, join, normpath
from urlparse import urlsplit
import urllib2
import json
import sys
import re

content_model = "http://schemas.usgin.org/uri-gin/ngds/dataschema/activefault/"

class Styles:

    def __init__(self):
        self.model_url = 'http://schemas.usgin.org/contentmodels.json'
        self.geoserver = Geoserver.from_ckan_config()

    def get_sld_dir(self):
        path = getcwd()
        parent = normpath(join(path, '..'))
        if 'sld_files' in listdir(parent):
        #if 'sld_files' not in listdir(parent):
        #    makedirs(join(parent, 'sld_files'))
            return join(parent, 'sld_files')
        else:
            error_msg = sys.exc_info()[0]
            return "Error: %s" % error_msg

    def get_gs_styles(self):
        geoserver = self.geoserver
        return [style.name for style in geoserver.get_styles()]

    def get_sld_list(self, path):
        this_path = path
        files = [f for f in listdir(this_path) if isfile(join(this_path,f)) if not f.startswith('.')]
        path_files = [join(this_path,f) for f in files]
        return path_files

    def get_dir_list(self, path):
        this_path = path
        dirs = [d for d in listdir(this_path) if isdir(join(this_path,d))]
        return dirs

    def make_file_path_list(self):
        these_paths = []
        base_dir = self.get_sld_dir()
        for paths, dirs, files in walk(base_dir):
            if len(dirs) == 0:
                these_paths.append(paths)
        return these_paths

    def make_sld_path_list(self):
        this_path = self.get_sld_dir()
        folders = self.get_dir_list(this_path)
        path_folders = [join(this_path, dir) for dir in folders]
        base_slds = self.get_sld_list(this_path)
        path_slds = [self.get_sld_list(that_path) for that_path in path_folders]
        flat_path_slds = [item for sub_list in path_slds for item in sub_list]
        all_sld_paths = base_slds + flat_path_slds
        return all_sld_paths

    def delete_default_styles(self):
        geoserver = self.geoserver
        default_styles = ['burg','capitals','cite_lakes','dem','giant_polygon','grass',
                          'green','line','poi','point','poly_landmarks','polygon',
                          'pophatch','population','rain','raster','restricted','simple_roads',
                          'simple_streams','tiger_roads']
        for style in default_styles:
            this_style = geoserver.get_style(style)
            geoserver.delete(this_style)

    def load_style(self, style_name, style_path):
        geoserver = self.geoserver
        styles = [style.name for style in geoserver.get_styles()]
        if style_name not in styles:
            geoserver.create_style(style_name, open(style_path).read(), overwrite=True)
        else:
            pass

    def loop_load_styles(self):
        this_path = self.get_sld_dir()
        files = self.get_sld_list()
        for file in files:
            style_name = file[:-4]
            style_path = this_path + file
            self.load_style(style_name, style_path)

    def get_content_models(self):
        url = self.model_url
        reader = urllib2.urlopen(url).read()
        data = json.loads(str(reader))
        return data

    def get_sld_uri(self, content_model=None):
        data = self.get_content_models()
        if content_model is None:
            return dict((model['label'], (version['uri'], version['sld_file_path']))
                        for model in data for version in model['versions'])
        else:
            return dict((model['label'], (version['uri'], version['sld_file_path'])) for model in
                        data for version in model['versions'] if model['uri'] == content_model)

    def get_sld(self, content_model=None):
        data = self.get_content_models()
        if content_model is None:
            return [model['sld_file_path'] for model in data for model in model['versions']]
        else:
            return [model['label'] for model in data if model['uri'] == content_model]

    def get_uri(self):
        data = self.get_content_models()
        return [model['uri'] for model in data for model in model['versions']]

    def build_file_directory(self):
        data = self.get_sld_uri()
        that_dir = self.get_sld_dir()
        urls = [value[1] for value in data.itervalues()]
        paths = [urlsplit(url).path for url in urls if url is not None]
        pattern_a = r'.*?\/files/(.*)/.*'
        path_id = [match.group(1) for path in paths for match in [re.search(pattern_a, path)]]
        pattern_b = re.compile('(-|\.)')
        path_safe_chars = [pattern_b.sub('_', path) for path in path_id]
        path_folders = [(path.rsplit('/')) for path in path_safe_chars]
        for path in path_folders:
            makedirs(join(that_dir, path[0], path[1]))

a = Styles()

#b = a.get_sld_dir()
#print a.get_dir_list(b)

print a.make_file_path_list()
