#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup

def is_package(path):
    return (
        os.path.isdir(path) and
        os.path.isfile(os.path.join(path, '__init__.py'))
        )

def find_packages(path, base="" ):
    """ Find all packages in path """
    packages = {}
    for item in os.listdir(path):
        dir = os.path.join(path, item)
        if is_package( dir ):
            if base:
                module_name = "%(base)s.%(item)s" % vars()
            else:
                module_name = item
            packages[module_name] = dir
            packages.update(find_packages(dir, module_name))
    return packages

def files_from(*paths, **kwargs):
    base = kwargs.pop('base')   
    def generator():
        for path in paths:
            path = os.path.join(base, path)
            print path
            
            if not os.path.isdir(path) or is_package(path): continue
                        
            for dir, _, files in os.walk(path):                            
                for file in files:                                       
                    yield os.path.relpath(os.path.join(dir, file),base)
                    
    return list(generator())

RESOURCE_PATHS = ('templates', 'static', 'media', 'locale', 'config')

def django_setup(project, apps=[], apps_dir='apps', package_dir = {}, packages = [], package_data = {}, **kwargs):
    
    # directories
    extra_dirs = dict( (app, os.path.join(apps_dir,app)) for app in apps )
    extra_dirs[project] = project
    package_dir.update(extra_dirs)
    
    # applications
    packages.extend(apps)
    # with all subpackages 
    for app in apps:
        packages.extend(find_packages(os.path.join(apps_dir, app), base=app))
    # and the project
    packages.append(project)
    
    # extra data        
    extra_data = {}
    for app in apps:
        extra_data[app] = files_from(*RESOURCE_PATHS, base=os.path.join(apps_dir, app))        
    extra_data[project] = files_from(*RESOURCE_PATHS, base=project)
    package_data.update(extra_data)   
    
    return setup(
                package_dir = package_dir, 
                packages = packages, 
                package_data = package_data, **kwargs)
    
#
# The reald stuff :)
#
django_setup(
    name='fnp-redakcja',
    version='1.1',
    description='IDE for developing books.',
    author="Fundacja Nowoczesna Polska",
    author_email='fundacja@nowoczesnapolska.org.pl',
    license="GNU Affero General Public License 3",
    maintainer='Łukasz Rekucki',    
    maintainer_email='lrekucki@gmail.com',
    url='http://github.com/fnp/redakcja',
    package_dir = {'': 'lib'},           
    py_modules = [ 
        'wlapi',
        'vstorage',    
    ],      
    scripts=[
        'scripts/crop.py', 
        'scripts/imgconv.py',
    ],             
    # django applications
    project = 'platforma',
    apps_dir = 'apps',
    apps = [
        'compress',
        'django_cas',   
        'filebrowser',
        'toolbar',
        'wiki',        
    ],
    # data_files=[ ('', ['LICENSE', 'NOTICE', 'README.rst', 'AUTHORS.md', 'requirements.txt'])],
)
