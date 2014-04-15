from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(
    name='ckanext-geoserver',
    version=version,
    description="Interface for adding Geoserver support and functionality to CKAN.",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Arizona Geological Survey',
    author_email='adrian.sonnenschein@azgs.az.gov',
    url='http://www.geothermaldata.gov',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.geoserver'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points={
        'ckan.plugins': [
            'geoserver=ckanext.geoserver.plugin:GeoserverPlugin',
            'ogc_preview=ckanext.ogc_preview.plugin:OGCPreviewPlugin',
        ]
    }
)
