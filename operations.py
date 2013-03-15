#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '3/15/13 10:23 AM'

import zipfile

class ReplaceZipFile(object):
    modify_list = None
    remove_list = None
    original = None
    target = None

    #handle
    input_file = None
    output_file = None

    def __init__(self, original, target):
        self.modify_list = {}
        self.remove_list = []
        self.original = original
        self.target = target

    def remove_file(self, filename):
        if filename not in self.remove_list:
            self.remove_list.append(filename)

        if filename in self.modify_list:
            del self.modify_list[filename]

    def write_file(self, archive_name, source_filename):
        with open(source_filename, 'rb') as file:
            return self.write_str(archive_name, file.read())

    def write_str(self, archive_name, buffer):
        if archive_name in self.remove_list:
            self.remove_list.remove(archive_name)

        self.modify_list[archive_name] = buffer

    def __enter__(self):
        self.input_file = zipfile.ZipFile(self.original, 'r')
        self.output_file = zipfile.ZipFile(self.target, 'w')

        self.input_file.__enter__()
        self.output_file.__enter__()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        input_file, self.input_file = self.input_file, None
        output_file, self.output_file = self.output_file, None

        written_file_list = []

        for item in input_file.infolist()[::-1]:
            if item.filename in self.remove_list:
                continue

            if item.filename in written_file_list:
                print 'skipping duplicated file entry:', item.filename
                continue

            written_file_list.append(item.filename)

            if item.filename in self.modify_list:
                buffer = self.modify_list[item.filename]
                del self.modify_list[item.filename]
            else:
                buffer = input_file.read(item.filename)

            output_file.writestr(item, buffer)

        self.modify_list = {}
        self.remove_list = []
        input_file.__exit__(exc_type, exc_val, exc_tb)
        output_file.__exit__(exc_type, exc_val, exc_tb)

        input_file.close()
        output_file.close()
