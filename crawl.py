#!/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary 

import time, json

browser = None
all_cats = []
list_not_added = []

class Cat:
	def __init__(self):
		self.name = None
		self.url = None
		self.prod_or_competence = []
		self.prods = []
	def to_json(self):
		return json.dumps(self.__dict__, sort_keys=True, indent=4)	

def q(css_sel):
	global browser
	return browser.find_elements_by_css_selector(css_sel)

def a_in_b(a, b):
	try:
		b.index(a)
		return True
	except:
		return False	

def crawl():
	global browser, all_cats, list_not_added
	browser.get("https://www.festool.ro/Products/Pages/Product-Overview.aspx")
	cats_raw = q("ul.four-col-list li.image-link-list-item")

	for cat_raw in cats_raw:
		cat = Cat()
		cat.name = cat_raw.find_elements_by_css_selector("div.title")[0].text.encode("utf-8")
		cat.url = cat_raw.find_elements_by_css_selector("a.link")[0].get_attribute("href").encode("utf-8")
		#print "CAT NAME : {0}, \nCAT URL : {1}".format(cat.name, cat.url)
		all_cats.append(cat)

	for cat in all_cats:
		browser.get(cat.url)
		if a_in_b("/Products/Pages/Product-Detail.aspx", browser.current_url): #direct product opened from overview
			cat.prods.append(browser.current_url)
		elif a_in_b("/Products/Pages/Product-Category.aspx", browser.current_url): #multiple products opened from overview
			prods_or_competences_raw = q("#content li.image-link-list-item a")
			for prod_or_competence_raw in prods_or_competences_raw:
				cat.prod_or_competence.append(prod_or_competence_raw.get_attribute("href"))
		elif a_in_b("/Products/Pages/Product-Competence.aspx", browser.current_url): #product competence opened from category		
			competences_raw = q("li.image-link-list-item a.link-btn")
			for competence_raw in competences_raw:
				if a_in_b("/Products/Pages/Product-Detail.aspx", competence_raw.get_attribute("href")):
					cat.prods.append(competence_raw.get_attribute("href"))
				else:
					list_not_added.append(competence_raw.get_attribute("href"))				

	for cat in all_cats:
		for prod_or_not in cat.prod_or_competence:
			browser.get(prod_or_not)
			if a_in_b("/Products/Pages/Product-Detail.aspx", browser.current_url):
				cat.prods.append(browser.current_url)
			elif a_in_b("/Products/Pages/Product-Competence.aspx", browser.current_url):	
				competences_raw = q("li.image-link-list-item a.link-btn")
				for competence_raw in competences_raw:
					if a_in_b("/Products/Pages/Product-Detail.aspx", competence_raw.get_attribute("href")):
						cat.prods.append(competence_raw.get_attribute("href"))
					else:
						list_not_added.append(competence_raw.get_attribute("href"))	
		#break				

	write_them_all()					
										
def write_them_all():
	global all_cats, list_not_added
	f = open("all_prods_in_cat.json", "a")
	f.write("\"42\":[")

	for cat in all_cats:
		f.write(cat.to_json() + ",\n")

	f.write("]")
	f.close()

	if len(list_not_added) > 0:
		f = open("other_stuff_not_saved.json", "a")
		for el in list_not_added:
			f.write(el + "\n")
		f.close()

def start():
	global browser 
	browser = webdriver.Chrome()
	crawl()


start()	
