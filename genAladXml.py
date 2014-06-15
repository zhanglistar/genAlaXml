#!/usr/bin/env python
#*-*encoding=utf-8*-*
########################################################################
# 
# Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
# 
########################################################################
 
'''
File: genAladXml.py
Author: zhanglistar(zhanglistar@baidu.com)
Date: 2014/06/13 21:54:46
'''
#!/usr/bin/python

START_LABEL="<"
LABEL_END_START="</"
END_LABEL=">\n"

import os
import sys
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

def defaultKeyComparator(keylist, key):
    for item in keylist:
        if item.find(key) >= 0:
            return True, item
    return False


class Merger(object):
    def __init__(self):
        self.xml_dict = {}

    def begin(self, sublabel, inxml_filename, keys, comparator):
        self.sublabel = sublabel
        self.input_xml = inxml_filename
        self.keys = keys
        self.comparator = comparator
    
    def merge(self):
        try:
            for event, elem in ET.iterparse(self.input_xml):
                if event == 'end':
                    if elem.tag == 'key':
                        flag,key = self.comparator(self.keys, elem.text.strip())
                        if flag == True:
                            str = START_LABEL + self.sublabel + END_LABEL
                            if key not in self.xml_dict.keys():
                                self.xml_dict[key] = str 
                            else:
                                self.xml_dict[key] += str
                        value_str = ""
                        continue
                    elif elem.tag == 'item':
                        self.xml_dict[key] += LABEL_END_START + self.sublabel + END_LABEL
                        value_str = ""
                    elif len(elem.text.strip()) > 0:
                        value_str += START_LABEL + elem.tag + END_LABEL + \
                                elem.text.strip() + \
                                LABEL_END_START + elem.tag + END_LABEL
        except Exception, e:
            raise e

    def merge_noec(self):
        for event, elem in ET.iterparse(self.input_xml):
            if event == 'end':
                if elem.tag == 'key':
                    flag,key = self.comparator(self.keys, elem.text.strip())
                    if flag == True:
                        str = START_LABEL + self.sublabel + END_LABEL
                        if key not in self.xml_dict.keys():
                            self.xml_dict[key] = str 
                        else:
                            self.xml_dict[key] += str
                    value_str = ""
                    continue
                elif elem.tag == 'item':
                    self.xml_dict[key] += value_str + LABEL_END_START + self.sublabel + END_LABEL
                    value_str = ""
                elif len(elem.text.strip()) > 0:
                    value_str += START_LABEL + elem.tag + END_LABEL + \
                            elem.text.strip() + \
                            LABEL_END_START + elem.tag + END_LABEL

    def serialize(self, filename):
        f = open(filename, 'w')
        for item in self.xml_dict.keys():
            f.write('<key>%s</key>\n' % item.encode('utf-8'))
            f.write('%s\n' % self.xml_dict[item].encode('utf-8'))
        f.close()

    def clean(self):
        self.xml_dict = {}


def main():
    # read conf
    key_list = []
    key_file = sys.argv[1]
    with open(key_file, "r") as f:
        for line in f:
            key_list.append(line.strip().decode('utf-8'))
    input_xml_file_conf = sys.argv[2]
    # read xml info
    input_xml_info_dict = {}
    with open(input_xml_file_conf, "r") as f:
        for line in f:
            line = line.strip().split(":")
            if line[0] in input_xml_info_dict.keys():
                raise Exception("site key dumplicate")
            input_xml_info_dict[line[0]] = line[1]
            
    # begin to merge
    merger_obj = Merger()
    for item in input_xml_info_dict.keys():
        merger_obj.begin(item, input_xml_info_dict[item], key_list, defaultKeyComparator)
        merger_obj.merge_noec()
    # end
    merger_obj.serialize(sys.argv[3])

if __name__ == '__main__':
    main()
