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
#import sys
from sys import platform as _platform
from pprint import pprint
import time, json, os

#reload(sys)  
#sys.setdefaultencoding('utf8')

from product import Product

USE_FIREFOX = False
internet_on = False
driver = None
scrapedLinks = []
assetsDir = "assets/"
productsDir = "prod/"

def readFileGetLinks():
	f = open("sitemap.txt", "r")
	return f.readlines()

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

def loadProductPage(url):
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
	driver.get(url)

def scrapeProduct(prod):

	global driver

	#common product attrs
	prod.href = driver.current_url
	prod.title = q("h1.title", "text")
	prod.subtitle = q("h2.subtitle", "text")
	prod.price = q("#ctl00_PlaceHolderMain_ctl37_PricePanel", "text")
	prod.img = stripParams(q("#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage", "src"))
	prod.variation = getProductVariation()
	prod.included = q(".product-detail-shipment ul", "text")
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
	prod.product_detail_performance_features_imgs = getImageSrcs(q(".product-detail-performance-features img.performance-feature-img", None))
	#end performance imgs
		
	#table with pdfs
	prod.product_pdfs_table = q("#ctl00_PlaceHolderMain_ctl26_UpdatePanel1 table", "html")

	#table with tehnical data
	displayStatus("Expanding product tehnical data", 0)
	prod.tehnical_data = executeWaitAndGet("#ctl00_PlaceHolderMain_ctl28_LbtnAllTechnicalData", 
		"__doPostBack('ctl00$PlaceHolderMain$ctl28$LbtnAllTechnicalData','')",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table tr:nth-child(4)",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table",
		"html")

	#product accessories
	prod.accessoriesLinks = getAccessoriesHrefs()

	#product consumables
	prod.consumablesLinks = getConsumablesHrefs()

	#download aseests
	saveProduct(prod)
	
def getProductVariations():
	if q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option", "len") > 0:
		return q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option", None)
	else:
		return None		
			
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
				elem = q(elem_to_get, None)[0]
			else:	
				elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, elem_expected)))[0]
			if what == "html":
				return elem.get_attribute("innerHTML")
			elif what == "text":
				return elem.text
			elif what == "src":
				return elem.get_attribute("src")
			elif what == "len":
				return len(elem)
			elif what == "self":
				return elem	
			else:
				return ""			
		except TimeoutException as tex:
			print "Timeout exception while waiting for : " + elem_expected
			print "Exception msg : " + str(tex.message)
			return ""
	else:
		return ""	
	
def getImageSrcs(img_list): #get all img srcs from html, return list
	x = []
	for el in img_list:
		x.append(el.get_attribute("src"))
	return x

def getAccessoriesHrefs():
	if q("#ctl00_PlaceHolderMain_ctl30_ctl00 div.system-accessory-item", "len") <= 0:
		displayStatus("No accessories to get...", 0)
		return None
	elif q("#ctl00_PlaceHolderMain_ctl30_ctl00 div.system-accessory-item", "len") > 0 and \
		q("#ctl00_PlaceHolderMain_ctl30_ctl00 div.system-accessory-item", "len") <= 6 and \
		q("#ctl00_PlaceHolderMain_ctl30_BtnAllSystemAccessories", "len") <= 0:
		displayStatus("Getting the accessories from this page...", 1)
		acc = q("#ctl00_PlaceHolderMain_ctl30_ctl00", None)[0]
	elif q("#ctl00_PlaceHolderMain_ctl30_BtnAllSystemAccessories", "len") >= 1:
		displayStatus("Getting accessories from accessories page...", 1)
		acc = executeWaitAndGet("#ctl00_PlaceHolderMain_ctl30_BtnAllSystemAccessories",
			"__doPostBack('ctl00$PlaceHolderMain$ctl30$LbtnAllSystemAccessories','')",
			"#ctl00_PlaceHolderMain_ctl34_ctl00 .system-accessory-item:nth-of-type(13)",
			"#ctl00_PlaceHolderMain_ctl34_ctl00",
			"self")
	else:
		return None

	hrefs = []
	for link in acc.find_elements_by_css_selector("a.styled-link"):
		hrefs.append(link.get_attribute("href"))

	goBackToProductPage()		
	return hrefs

def getConsumablesHrefs():
	if q("#ctl00_PlaceHolderMain_ctl32_ctl00 div.consumables-item", "len") <= 0:
		displayStatus("No consumables to get...", 0)
		return None
	elif q("#ctl00_PlaceHolderMain_ctl32_ctl00 div.consumables-item", "len") > 0 and \
		q("#ctl00_PlaceHolderMain_ctl32_ctl00 div.consumables-item", "len") <= 6 and \
		q("#ctl00_PlaceHolderMain_ctl32_BtnAllConsumables", "len") <= 0:
		displayStatus("Getting the consumables from this page...", 1)
		acc = q("#ctl00_PlaceHolderMain_ctl32_ctl00", None)[0]
	elif q("#ctl00_PlaceHolderMain_ctl32_BtnAllConsumables", "len") >= 1:
		displayStatus("Getting consumables from consumables page...", 1)
		acc = executeWaitAndGet("#ctl00_PlaceHolderMain_ctl32_BtnAllConsumables",
			"__doPostBack('ctl00$PlaceHolderMain$ctl32$LbtnAllConsumables','')",
			"#ctl00_PlaceHolderMain_ctl36_ctl00 .consumables-item:nth-of-type(13)",
			"#ctl00_PlaceHolderMain_ctl36_ctl00",
			"self")
	else:
		return None

	hrefs = []
	for link in acc.find_elements_by_css_selector(".consumables-item a.styled-link"):
		hrefs.append(link.get_attribute("href"))

	goBackToProductPage()		
	return hrefs

def goBackToProductPage():
	displayStatus("Going back to product page...", 0)
	if q("#ctl00_PlaceHolderMain_ctl36_LbtnAllConsumables", "len") >= 1:
		executeWaitAndGet("#ctl00_PlaceHolderMain_ctl36_LbtnAllConsumables", 
			"__doPostBack('ctl00$PlaceHolderMain$ctl36$LbtnAllConsumables','')",
			"#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage",
			"#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage",
			"self")
	elif q("#ctl00_PlaceHolderMain_ctl34_LbtnAllSystemAccessories", "len") >= 1:			
		executeWaitAndGet("#ctl00_PlaceHolderMain_ctl34_LbtnAllSystemAccessories", 
			"__doPostBack('ctl00$PlaceHolderMain$ctl34$LbtnAllSystemAccessories','')",
			"#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage",
			"#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage",
			"self")

def stripParams(url):
	if url is not None:
		return url[0:url.index("?")]	
	else:
		return ""	
	
def mkdir(name):
	if not os.path.exists(name):
		os.makedirs(name)

def downloadFile(urlToRetrieve, dirName):
	file = urllib2.urlopen(urlToRetrieve).read()
	with open(dirName, "wb") as localFile:
		localFile.write(file)

def saveProduct(prod):
	displayStatus("Downloading product assets...", 1)
	fileName = (prod.title + "_" + prod.subtitle + "_" + prod.variation).decode("utf-8").replace(" ", "-").lower()
	try:
		mkdir(fileName)
		downloadFile(prod.img, \
			fileName + "/" + prod.img[prod.img.rindex("/") + 1:]) #download image and save as filename reverse index of .
	except Exception as ex:
		displayStatus(str(ex), -1)
		pass

	#save to json file
	displayStatus("Saving product...", 1)
	f = open(fileName + ".json", "w")
	f.write(prod.to_json().encode('utf8'))
	f.close()

def displayStatus(msg, color):
	global driver
	if color == 1:
		colors = "limegreen"
	elif color == 0:
		colors = "orange"
	elif color == -1:
		colors = "red"	
	else: 
		colors = "red"
	print "Status [{0}] : {1}".format(color, msg)			
	driver.execute_script("$(\"#alert\").remove(); $(\"body\").append(\"<div id='alert' " \
		"style='position:fixed;bottom:20px;right:20px;background:{0};padding:15px 20px; " \
		"color:#fff;font-size:14px;border-radius:5px;'>{1}</div>\");".format(colors, msg))

def speak(what):
	if _platform.startswith("linux"):
		# linux
		import subprocess
		subprocess.call(['speech-dispatcher'])
		subprocess.call(['spd-say', what])
	elif _platform.startswith("darwin"):
		# MAC OS X
		os.system("say " + what)
	elif _platform == "win32":
		# Windows
		import winsound
		freq = 2500 # Set Frequency To 2500 Hertz
		dur = 1000 # Set Duration To 1000 ms == 1 second
		winsound.Beep(freq, dur)

def clearScreen():
	import os
	if _platform.startswith("linux") or _platform.startswith("darwin"):
		# linux or mac
		os.system("clear")
	else:
		# windows
		os.system("cls")

def __init__():
	clearScreen()
	global driver
	if (USE_FIREFOX):
		binary = FirefoxBinary('/usr/bin/firefox') 
		driver = webdriver.Firefox() #.Firefox(firefox_binary=binary) 
	else:	
		driver = webdriver.Chrome()

	loadProductPage("https://www.festool.ro/Products/Pages/Product-Detail.aspx?pid=561184&name=Ferastrau-circular-TS-75-EBQ")
	prod = Product()
	if getProductVariations() is not None:
		lastVariation = q("body", "html")
		for i in range(len(getProductVariations())):
			if getProductVariations()[i].get_attribute("value") == "":
				scrapeProduct(prod)
				continue
			displayStatus("Switching product variation...", 0)
			getProductVariations()[i].click()
			while getProductVariation() == lastVariation:
				time.sleep(0.5)
			lastVariation = getProductVariation()	
			scrapeProduct(prod)
	else:
		#scrapeProduct(prod)
		print "NO " + getProductVariations()
		pass

	#scrapeProduct("https://www.festool.ro/Products/Pages/Product-Detail.aspx?pid=561184&name=Ferastrau-circular-TS-75-EBQ")   #-- 8 consumables in new tab :(
	#driver.close()	

__init__()	