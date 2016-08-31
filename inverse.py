#!/bin/python
# -*- coding: utf-8 -*-
from pprint import pprint #pretty print json
import os, time, json

list_of_all_acc = []

class Acc(object):
	"""docstring for acc"""
	def __init__(self, name):
		self.name = name
		self.parents = []
	def to_json(self):
		return json.dumps(self.__dict__, sort_keys=False, indent=4)

def init():
	f = open("relationships.json", "r")
	j = json.load(f)
	for elem in j["42"]: #loop objs
		for name in elem["children"]: #loop childs
			#print elem["children"]
			if not acc_in_list(name): #if acc with name does not exist
				#print "if not acc_in_list(name)"
				acc = Acc(name) #make one
				if elem["name"] not in acc.parents:	#if parent not added to it
					#print "if elem[name] not in acc.parents"
					acc.parents.append(elem["name"]) #add parent
			else: #if acc did exist
				acc = get_acc_with_name(name) #get him by his name
				if elem["name"] not in acc.parents:	#if parent not added to it
					acc.parents.append(elem["name"]) #add parent

			list_of_all_acc.append(acc) #add acc to big list

	f = open("i_relationships.json", "w")
	f.write("{\"42\":[")
	for acc in list_of_all_acc:
		f.write(acc.to_json() + ",\n")
	f.write("]}")
	f.close()

def acc_in_list(acc):
	for elem in list_of_all_acc:
		if elem.name == acc:
			return True
	return False

def get_acc_with_name(name):
	for acc in list_of_all_acc:
		if acc.name == name:
			return acc

	return None

init()