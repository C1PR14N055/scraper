#!/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary 
''' WAIT FOR EXPECTED CONDITIONS IMPORTS '''
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
''' END WAIT FOR EXPECTED CONDITIONS IMPORTS '''
''' URLLIB2 FOR CHECKING CONN '''
import urllib2
''' URLLIB2 FOR CHECKING CONN '''
from sys import platform as _platform
from pprint import pprint
import time

from product import Product

USE_FIREFOX = False
internet_on = False
driver = None
scrapedLinks = []

def writeFile(text):
	f = open("prod.txt", "w")
	f.write(text.encode('utf8'))
	f.close()

def	q(selector, what): #select html elements by css selector
	global driver
	if what == "html":
		return driver.find_elements_by_css_selector(selector)[0].get_attribute("innerHTML") \
		if driver.find_elements_by_css_selector(selector) is not None else None
	elif what == "text":
		return driver.find_elements_by_css_selector(selector)[0].text \
		if driver.find_elements_by_css_selector(selector) is not None else None
	elif what == "src":
		return driver.find_elements_by_css_selector(selector)[0].get_attribute("src") \
		if driver.find_elements_by_css_selector(selector) is not None else None
	elif what == "len":
		return len(driver.find_elements_by_css_selector(selector)) \
		if driver.find_elements_by_css_selector(selector) is not None else -1
	else:
		return driver.find_elements_by_css_selector(selector) \
		if driver.find_elements_by_css_selector(selector) is not None else None		
	
def scrapeProduct():
	global internet_on
	while not internet_on:
		try:
			resp = urllib2.urlopen("http://google.ro", timeout=1)
			internet_on = True
			break
		except:
			internet_on = False	
			speak("Internet connection not available!")
			time.sleep("10.0")

	global driver
	driver.get("https://www.festool.ro/Products/Pages/Product-Detail.aspx?pid=564636")
	prod = Product() #new Product object

	if not isProductPage():
		driver.execute_script("__doPostBack('ctl00$PlaceHolderMain$ctl34$LbtnAllSystemAccessories','');")
		displayStatus("Going to product page", 0)
		while not isProductPage:
			time.sleep(0.5)
	
	displayStatus("Scraping product page...", 1)

	#common product attrs
	prod.title = q("h1.title", "text")
	prod.subtitle = q("h2.subtitle", "text")
	prod.price = q("#ctl00_PlaceHolderMain_ctl37_PricePanel", "text")
	prod.img = q("#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage", "src")
	prod.variation = getProductVariation()
	#end common product attrs

	#product details
	prod.product_details_title = q(".product-detail-txt h3.title", "text")
	prod.product_details = q("ul.detail-txt-list", "text")
	prod.product_detail_common_attributes_title = q(".product-detail-common-attributes h3.title", "text")
	prod.product_detail_common_attributes = q("ul.common-attributes-list", "text")
	prod.product_detail_primary_uses_title = q(".product-detail-primary-uses h3.title", "text")
	prod.product_detail_primary_uses = q("ul.primary-uses-list", "text")
	#end product details

	#performance imgs
	prod.product_detail_performance_features = ", ".join(getImageSrcs(q(".product-detail-performance-features img.performance-feature-img", None)))
	#end performance imgs
		
	#table with pdfs
	prod.product_pdfs_table = q("#ctl00_PlaceHolderMain_ctl26_UpdatePanel1 table", "html")


	#table with tehnical data
	prod.tehnical_data = executeWaitAndGet("#ctl00_PlaceHolderMain_ctl28_LbtnAllTechnicalData", 
		"__doPostBack('ctl00$PlaceHolderMain$ctl28$LbtnAllTechnicalData','')",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table tr:nth-child(4)",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table",
		"html")

	#print prod.tehnical_data[0].get_attribute("innerHTML")
	writeProduct(prod)
	
def getProductHasVariations():
	if q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection select option", "len") > 0:
		return True
	else False		
			
def getProductVariation(): #curent prod variation
	if q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection", "len") >= 1:
		return q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option[selected]", "text")

def executeWaitAndGet(elem_exists, js_to_exec, elem_expected, elem_to_get, what):
	global driver
	if q(elem_exists, None):
		driver.execute_script(js_to_exec)
		try:
			if elem_to_get is not None:
				WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, elem_expected)))
				elem = q(elem_to_get, None)
			else:	
				elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, elem_expected)))
			if what == "html":
				return elem.get_attribute("innerHTML")
			elif what == "text":
				return elem.text
			elif what == "src":
				return elem.get_attribute("src")
			elif what == "len":
				return len(elem)
			else:
				return ""			
		except TimeoutException:
			print "Timeout exception while waiting for : " + elem_expected
			return ""
	else:
		return ""	

def isProductPage():
	if q("#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage", "len") >= 1:
		return True
	else:
		return False	

def isProductAccesoriesPage():
	if q("#ctl00_PlaceHolderMain_ctl34_ctl00 div.system-accessory-item", "len") > 6 and not isProductPage():
		return True
	else:
		return False
	
def getImageSrcs(list): #get all img srcs from html, return list
	x = []
	for el in list:
		x.append(el.get_attribute("src"))
	return x

def stripParams(url):
	return url[0:url.index("?")]	
	
def writeProduct(prod):
	if False: #debug
		pprint(vars(prod))
		print "\nTables with pdfs: " + prod.product_pdfs_table[0].text
		return
	writeFile("Titlu: " + prod.title + "\nSubtitlu: " + prod.subtitle + "\nPret: " + prod.price 
		+ "\nSursa imagine: " + prod.img + "\nTitlu descriere: " + prod.product_details_title
		+ "\nDescriere: " + prod.product_details + "\nTitlu caracteristici: " + prod.product_detail_common_attributes_title
		+ "\nCaracteristici: " + prod.product_detail_common_attributes + "\nTitlu atribuitari: " + prod.product_detail_primary_uses_title
		+ "\nAtribuintari: " + prod.product_detail_primary_uses + "\nPerf. features: " + prod.product_detail_performance_features
		+ "\nTables with pdfs: " + prod.product_pdfs_table + "\nTehnical data: " + prod.tehnical_data)

def displayStatus(msg, color):
	global driver
	if color == 1:
		color = "limegreen"
	elif color == 0:
		color = "orange"
	elif color == -1:
		color = "red"	
	else: 
		color = "red"		
	driver.execute_script("$(\"#alert\").remove(); $(\"body\").append(\"<div id='alert' " \
		"style='position:fixed;bottom:20px;right:20px;background:{0};padding:15px 20px; " \
		"color:#fff;font-size:14px;border-radius:5px;'>{1}</div>\");".format(color, msg))

def speak(what):
	if _platform.startswith("linux"):
		# linux
		import subprocess
		subprocess.call(['speech-dispatcher'])
		subprocess.call(['spd-say', what])
	elif _platform.startswith("darwin"):
		# MAC OS X
		import os
		os.system("say " + what)
	elif _platform == "win32":
		# Windows
		import winsound
		freq = 2500 # Set Frequency To 2500 Hertz
		dur = 1000 # Set Duration To 1000 ms == 1 second
		winsound.Beep(freq, dur)


def __init__():
	global driver
	if (USE_FIREFOX):
		binary = FirefoxBinary('/usr/bin/firefox') 
		driver = webdriver.Firefox() #.Firefox(firefox_binary=binary) 
	else:	
		driver = webdriver.Chrome()

	scrapeProduct()
	#driver.close()	

__init__()	
#elem.send_keys("")
#elem.send_keys(Keys.RETURN)
#assert "No results found." not in driver.page_source
