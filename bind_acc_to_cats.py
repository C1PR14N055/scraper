#!/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint #pretty print json
import os, time, json


list_of_all_items = []

class Item(object):
    """docstring for Item"""
    def __init__(self, name):
        self.name = name
        self.children = []

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=True, indent=4)

def cat_has_acc():
    rootDir = './prod/'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            #print('\t%s' % fname) 
            if fname == "prod.json":
                #print dirName + " >> " + fname
                with open(dirName + "/" + fname) as data_file:    
                    prod = json.load(data_file)
                #print "> " + prod["title"].encode("utf-8")
                i = Item((prod["title"] + " " + prod["subtitle"]).encode("utf-8"))

                #print "dirName " + dirName
                for dirName2, subdirList2, fileList2 in os.walk(dirName, topdown=False): 
                    for fname2 in fileList2:
                        if fname2 == "acc.json":
                            #print dirName + " >> " + fname
                            with open(dirName2 + "/" + fname2) as data_file2:    
                                acc = json.load(data_file2)
                            #print "\t> " + acc["title"].replace("\n", "").encode("utf-8")
                            i.children.append(acc["title"].encode("utf-8"))
                list_of_all_items.append(i)

    f = open("relationships.json", "a")
    f.write("\"42\":[")

    for item in list_of_all_items:
        f.write(item.to_json() + ",\n")

    f.write("]")
    f.close()

cat_has_acc()