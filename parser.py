#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""entry of program
"""

__author__ = 'johnx'
__date__ = '3/15/13 7:39 AM'

import yaml
import os
from operations import ReplaceZipFile
import time

_BASE_DIR = None
_CONFIG_DIR = 'data/config'
_CONFIG_DIR_BASE = '.base'
_ICON_DIR = 'data/icons'
_ICON_DIR_AUTO = '.auto'
_INSTALL_DIR = r'E:\Program Files (x86)\JetBrains\PhpStorm 6.0'
_BUILD_FILE = 'build.txt'
_TMP_FILE = '~icon_replace.tmp'
_BACKUP_DIR = 'backup'

def lookup_yaml(path):
    path = os.path.join(_CONFIG_DIR, path)
    file_list = os.listdir(os.path.join(_CONFIG_DIR, path))
    full_filenames = map(lambda filename: os.path.join(path, filename), file_list)
    yaml_filter = lambda filename: \
                            filename.endswith('.yaml') \
                        and not filename.split(os.sep)[-1].startswith('.') \
                        and os.path.isfile(filename) \
                        and os.access(filename, os.R_OK)
    yaml_list = filter(yaml_filter, full_filenames)

    return yaml_list

def run():
    #load yaml list
    #parse & merge modify request
    #do patch jar
    #replace jar

    yaml_list = lookup_yaml(os.path.join(_CONFIG_DIR, _CONFIG_DIR_BASE))
    for filename in yaml_list:
        with open(filename, 'rb') as file:
            process_yaml(file)

def process_yaml(yaml_file):
    request = yaml.load(yaml_file)
    source_path = os.path.join(_ICON_DIR, request['source'])
    source_path_auto = os.path.join(source_path, _ICON_DIR_AUTO)
    target_path = os.path.join(_INSTALL_DIR, request['target'])
    actions = request['actions']
    auto_replace = actions['auto_replace']

    with ReplaceZipFile(target_path, _TMP_FILE) as zipfile:
        if auto_replace:
            for top, dirs, files in os.walk(source_path_auto):
                rel_path = os.path.relpath(top, source_path_auto)
                for filename in files:
                    full_path = os.path.join(top, filename)
                    if not os.path.isfile(full_path) or not os.access(full_path, os.R_OK):
                        continue

                    if filename == '.skip.me.tmp':
                        continue

                    rel_name = os.path.join(rel_path, filename).replace(os.sep, '/')
                    print 'writing auto replace: ', rel_name, full_path
                    zipfile.write_file(rel_name, full_path)

        for source_icon, archive_icon in actions['replace']:
            source_icon = os.path.join(source_path, source_icon)
            if not os.path.isfile(source_icon) or not os.access(source_icon, os.R_OK):
                print 'cannot access source icon: [%s]' % source_icon
                continue

            zipfile.write_file(archive_icon, source_icon)

    backup_dir = os.path.dirname(os.path.join(_BACKUP_DIR, request['target']))
    if not os.path.isdir(backup_dir):
        os.mkdir(backup_dir)
    os.rename(target_path, os.path.join(_BACKUP_DIR, request['target']))
    os.rename(_TMP_FILE, target_path)

def dump_version():
    build_file = os.path.join(_INSTALL_DIR, _BUILD_FILE)
    if os.path.isfile(build_file) and os.access(build_file, os.R_OK):
        with open(build_file, 'rb') as file:
            return file.read()

    return None

if __name__ == '__main__':
    _BASE_DIR = os.path.abspath(os.path.dirname(__file__)).replace('/', os.sep)
    _CONFIG_DIR = os.path.join(_BASE_DIR, _CONFIG_DIR).replace('/', os.sep)
    _ICON_DIR = os.path.join(_BASE_DIR, _ICON_DIR).replace('/', os.sep)

    session_name = 'session-%s' % time.time()
    _BACKUP_DIR = os.path.join(_BASE_DIR, _BACKUP_DIR, session_name).replace('/', os.sep)
    if not os.path.isdir(_BACKUP_DIR):
        os.mkdir(_BACKUP_DIR)

    print `dump_version()`

    run()
