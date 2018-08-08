# -*- coding: utf-8 -*-
# @File  : xmltojson.py
# @Author: jiawen
# @time: 18-7-30 下午2:57
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom


class xmltojson:
    SHOW_LOG = True
    XML_PATH = None
    a = {}
    m = []

    def get_root(self, path):
        tree = ET.fromstring(path)
        return tree

    def get_element_tag(self, element):
        if element is not None:
            return element.tag
        else:
            print('the element is None!')

    def get_element_attrib(self, element):
        if element is not None:
            return element.attrib
        else:
            print('the elemrnt is None!')

    def get_element_text(self, element):
        if element is not None:
            return element.text
        else:
            print('the element is None!')

    def get_element_children(self, element):
        if element is not None:
            return [c for c in element]
        else:
            print('the element is None!')

    def get_elements_tag(self, elements):
        if elements is not None:
            tags = []
            for e in elements:
                tags.append(e.tag)
            return tags
        else:
            print('the elenemts is None!')

    def get_elements_attrib(self, elements):
        if elements is not None:
            attribs = []
            for a in elements:
                attribs.append(a.attrib)

            return attribs
        else:
            print('the elements is None!')

    def get_elements_text(self, elements):
        if elements is not None:
            text = []
            for t in elements:
                text.append(t.text)
            return dict(zip(self.get_elements_tag(elements), text))
        else:
            print('the elements is None!')

    def main(self, xml):
        root = self.get_root(xml)
        children = self.get_element_children(root)
        children_tags = self.get_elements_tag(children)
        children_attribs = self.get_elements_attrib(children)
        i = 0
        for c in children:
            p = 0
            c_children = self.get_element_children(c)
            dict_text = self.get_elements_text(c_children)
            if dict_text:
                if children_tags[i] == 'TemplateSMS':
                    self.a['templateSMS'] = dict_text
                else:
                    if children_tags[i] == 'SubAccount':
                        K = 0
                        for x in children:
                            if children_tags[k] == 'totalCount':
                                self.m.append(dict_text)
                                self.a['SubAccount'] = self.m
                                p = 1
                            k = k + 1
                        if p == 0:
                            self.a[children_tags[i]] = dict_text
                    else:
                        self.a[children_tags[i]] = dict_text
            else:
                self.a[children_tags[i]] = c.text
            i = i + 1
            return self.a

    def main2(self, xml):
        # root
        root = self.get_root(xml)

        # children
        children = self.get_element_children(root)

        children_tags = self.get_elements_tag(children)

        children_attribs = self.get_elements_attrib(children)

        i = 0

        # 获取二级元素的每一个子节点的名称和值
        for c in children:
            p = 0
            c_children = self.get_element_children(c)
            dict_text = self.get_elements_text(c_children)
            if dict_text:
                if children_tags[i] == 'TemplateSMS':
                    k = 0

                    for x in children:
                        if children_tags[k] == 'totalCount':
                            self.m.append(dict_text)
                            self.a['TemplateSMS'] = self.m
                            p = 1
                        k = k + 1
                    if p == 0:
                        self.a[children_tags[i]] = dict_text
                else:
                    self.a[children_tags[i]] = dict_text

            else:
                self.a[children_tags[i]] = c.text
            i = i + 1
        return self.a
