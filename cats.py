#!/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint #pretty print json

import os, time, json

list_of_cats = []

def get_cats():
    rootDir = './prod/'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        #print('Found directory: %s' % dirName)
        for fname in fileList:
            #print('\t%s' % fname) 
            if fname == "prod.json":
                #print dirName + " >> " + fname
                with open(dirName + "/" + fname) as data_file:    
                    prod = json.load(data_file)
                if prod["parent_name"] not in list_of_cats:
                    list_of_cats.append(prod["parent_name"])

    for cat in list_of_cats:
        print cat

    #j = json.dumps(list_of_cats)    
    #pprint(j)            


get_cats()