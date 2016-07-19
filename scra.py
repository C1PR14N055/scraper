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
from accessorie import Accessorie

USE_FIREFOX = False
internet_on = False
driver = None
scrapedLinks = []
assetsDir = "assets/"
productsDir = "prod/"
#accDir = "acc/"
#consDir = "cons/"

def readFileGetLinks():
	f = open("sitemap.txt", "r")
	return f.readlines()

def	q(selector, what): #select html elements by css selector
	global driver
	if what == "html":
		return driver.find_elements_by_css_selector(selector)[0].get_attribute("innerHTML").encode("utf-8") \
		if len(driver.find_elements_by_css_selector(selector)) > 0 else None
	elif what == "text":
		return driver.find_elements_by_css_selector(selector)[0].text.encode("utf-8") \
		if len(driver.find_elements_by_css_selector(selector)) > 0 else None
	elif what == "src":
		return driver.find_elements_by_css_selector(selector)[0].get_attribute("src") \
		if len(driver.find_elements_by_css_selector(selector)) > 0 else None
	elif what == "len":
		return len(driver.find_elements_by_css_selector(selector)) \
		if len(driver.find_elements_by_css_selector(selector)) > 0 else -1
	else:
		return driver.find_elements_by_css_selector(selector) \
		if len(driver.find_elements_by_css_selector(selector)) > 0 else None		

def a_in_b(a, b):
	try:
		b.index(a)
		return True
	except:
		return False

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
	prod.href = str(driver.current_url)
	prod.title = str(q("h1.title", "text"))
	prod.subtitle = str(q("h2.subtitle", "text"))
	prod.price = str(q("#ctl00_PlaceHolderMain_ctl37_PricePanel", "text"))
	prod.img = str(stripParams(q("#ctl00_PlaceHolderMain_ctl16_ImgProductDetailImage", "src")))
	prod.variation = str(getProductVariation())
	prod.included = str(q(".product-detail-shipment ul", "text"))
	#end common product attrs

	#product details
	prod.product_details_title = str(q(".product-detail-txt h3.title", "text"))
	prod.product_details = str(q("ul.detail-txt-list", "text"))
	prod.product_detail_common_attributes_title = str(q(".product-detail-common-attributes h3.title", "text"))
	prod.product_detail_common_attributes = str(q("ul.common-attributes-list", "text"))
	prod.product_detail_primary_uses_title = str(q(".product-detail-primary-uses h3.title", "text"))
	prod.product_detail_primary_uses = str(q("ul.primary-uses-list", "text"))
	#end product details

	#performance imgs
	prod.product_detail_performance_features_imgs = getImageSrcs(q(".product-detail-performance-features img.performance-feature-img", None))
		
	#table with pdfs
	prod.product_pdfs_table = str(q("#ctl00_PlaceHolderMain_ctl26_UpdatePanel1 table", "html"))

	#table with tehnical data
	displayStatus("Expanding product tehnical data", 0)
	prod.tehnical_data = str(executeWaitAndGet("#ctl00_PlaceHolderMain_ctl28_LbtnAllTechnicalData", 
		"__doPostBack('ctl00$PlaceHolderMain$ctl28$LbtnAllTechnicalData','')",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table tr:nth-child(4)",
		"#ctl00_PlaceHolderMain_ctl28_ctl00 table",
		"html"))

	#product accessories
	prod.accessoriesLinks = getAccessoriesHrefs()

	#product consumables
	prod.consumablesLinks = getConsumablesHrefs()

	#download assets
	saveProduct(prod)

	saveAssets(prod.product_detail_performance_features_imgs)
	
def scrapeAccessorie(prod, as_cons=False):
	global driver

	if a_in_b("/Products/Accessories/Pages/Variations.aspx", driver.current_url):
		acc_vars = q(".consumable_col_link a", None)
		acc_urls = []
		for acc_var in acc_vars:
			acc_urls.append(acc_var.get_attribute("href"))
		for acc_url in acc_urls:
			acc = Accessorie()
			#print acc_url
			driver.execute_script(acc_url)
			#common product attrs
			acc.href = str(driver.current_url)
			acc.title = str(q(".product-detail-title", "text"))
			acc.price = str(q("#ctl00_PlaceHolderMain_ctl33_PricePanel", "text"))
			acc.img = str(stripParams(q("#ctl00_PlaceHolderMain_ctl20_ProductImage", "src")))
			acc.included = str(q("#ctl00_PlaceHolderMain_ctl19_UpdatePanel1", "text"))
			#end common product attrs

			#product details
			acc.product_details = str(q("#ctl00_PlaceHolderMain_ctl21_UpdatePanel1", "text"))

			#table with tehnical data
			displayStatus("Expanding product tehnical data", 0)
			acc.tehnical_data = str(q("#ctl00_PlaceHolderMain_ctl23_UpdatePanel1", "html"))

			#download aseests
			saveAccessorie(acc, prod, as_cons) 
			driver.back()
	else:
		acc = Accessorie()
		#common product attrs
		acc.href = str(driver.current_url)
		acc.title = str(q(".product-detail-title", "text"))
		acc.price = str(q("#ctl00_PlaceHolderMain_ctl33_PricePanel", "text"))
		acc.img = str(stripParams(q("#ctl00_PlaceHolderMain_ctl20_ProductImage", "src")))
		acc.included = str(q("#ctl00_PlaceHolderMain_ctl19_UpdatePanel1", "text"))
		#end common product attrs

		#product details
		acc.product_details = str(q("#ctl00_PlaceHolderMain_ctl21_UpdatePanel1", "text"))

		#table with tehnical data
		displayStatus("Expanding product tehnical data", 0)
		acc.tehnical_data = str(q("#ctl00_PlaceHolderMain_ctl23_UpdatePanel1", "html"))

		#download aseests
		saveAccessorie(acc, prod, as_cons) 	

def isAccessoriesPage():
	global driver
	try:
		if driver.current_url.index("festool.ro/Products/Accessories") != -1:
			return True
		else:
			return False
	except:
		return False	

def isProductPafe():
	global driver
	try:
		if driver.current_url.index("festool.ro/Products/Pages/Product-Detail.aspx") != -1:
			return True
		else:
			return False	
	except:
		return False			

def getProductVariations(): #all product variations
	if q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option", "len") > 0:
		return q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option", None)
	#elif q("#ctl00$PlaceHolderMain$ctl12$DdlProductVariantSelection option", "len") > 0:
		#return q("#ctl00$PlaceHolderMain$ctl12$DdlProductVariantSelection option", None)	
	else:
		return None		
			
def getProductVariation(): #curent prod variation
	if q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection", "len") >= 1:
		return q("#ctl00_PlaceHolderMain_ctl12_DdlProductVariantSelection option[selected]", "text")
	#elif q("#ctl00$PlaceHolderMain$ctl12$DdlProductVariantSelection", "len") >= 1:
		#return q("#ctl00$PlaceHolderMain$ctl12$DdlProductVariantSelection option[selected]", "text")
	else: return None	

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
				return elem.get_attribute("innerHTML").encode("utf-8")
			elif what == "text":
				return elem.text.encode("utf-8")
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
	if img_list is None:
		return None
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

def saveAssets(assetsList):
	if assetsList is not None and len(assetsList) > 0:
		for asset in assetsList:
			if not os.path.isfile(assetsDir + asset[asset.rindex("/") + 1:]):
				downloadFile(stripParams(asset), stripParams(assetsDir + asset[asset.rindex("/") + 1:]))

def downloadFile(urlToRetrieve, dirName):
	file = urllib2.urlopen(urlToRetrieve).read()
	with open(dirName, "wb") as localFile:
		localFile.write(file)

def saveProduct(prod):
	displayStatus("Downloading product assets...", 1)
	fileName = (prod.title + "_" + prod.subtitle).decode("utf-8").replace(" ", "-").lower()
	try:
		mkdir(productsDir)
		mkdir(assetsDir)
		mkdir(productsDir + fileName)
		downloadFile(prod.img, \
			productsDir + fileName + "/" + prod.img[prod.img.rindex("/") + 1:]) #download image and save as filename = reverse index of .
	except Exception as ex:
		displayStatus(str(ex), -1)
		pass

	#save to json file
	displayStatus("Saving product...", 1)
	f = open(productsDir + fileName + "/" + "prod.json", "w")
	f.write(prod.to_json().encode('utf8'))
	f.close()

def saveAccessorie(acc, prod, as_cons=False):
	if as_cons:
		accDir = "cons/"
	else:
		accDir = "acc/"	
	displayStatus("Downloading accessorie assets...", 1)
	fileName = (prod.title + "_" + prod.subtitle + "_" + prod.variation).decode("utf-8").replace(" ", "-").replace("/", "-").lower()
	fileNameAcc = (acc.title).decode("utf-8").replace(" ", "-").replace("/", "-").lower()

	try:
		mkdir(productsDir)
		mkdir(assetsDir)
		mkdir(productsDir + fileName + "/" + accDir + fileNameAcc)
		downloadFile(acc.img, \
			productsDir + fileName + "/" + accDir + fileNameAcc + "/" + acc.img[acc.img.rindex("/") + 1:]) #download image and save as filename reverse index of /
	except Exception as ex:
		displayStatus(str(ex), -1)
		pass

	#save to json file
	displayStatus("Saving accessorie...", 1)
	f = open(productsDir + fileName + "/" + accDir + fileNameAcc + "/" + "acc.json", "w")
	f.write(acc.to_json().encode('utf8'))
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
		os.system("say -v Fred " + what)
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
	
	#try:
	clearScreen()
	global driver
	if (USE_FIREFOX):
		binary = FirefoxBinary('/usr/bin/firefox')
		driver = webdriver.Firefox() #.Firefox(firefox_binary=binary) 
	else:	
		driver = webdriver.Chrome()

	with open("all_prods_in_cat.json") as json_file:
		json_data = json.load(json_file)

	for categ in json_data:
		for produ in categ["prods"]:
			loadProductPage(produ)
			prod = Product()
			prod.parent_name = categ["name"]
			prod.parent_url = categ["url"]

			if getProductVariations() is not None: #prod does has variations
				lastVariation = q("body", "html")
				for i in range(len(getProductVariations())):
					if getProductVariations()[i].get_attribute("value") == "": #if product variation = default
						
						scrapeProduct(prod)

						if prod.accessoriesLinks is not None \
							and len(prod.accessoriesLinks) > 0:		#if prod has accessories
							for j in range(len(prod.accessoriesLinks)):
								loadProductPage(prod.accessoriesLinks[j].encode("utf-8"))
								scrapeAccessorie(prod)
								driver.back()

						if prod.consumablesLinks is not None \
							and len(prod.consumablesLinks) > 0:		#if prod has consumables
							for j in range(len(prod.consumablesLinks)):
								loadProductPage(prod.consumablesLinks[j].encode("utf-8"))
								scrapeAccessorie(prod, True)
								driver.back()		
						continue
					displayStatus("Switching product variation...", 0)
					getProductVariations()[i].click()
					while q("body", "html") == lastVariation:
						time.sleep(0.5)
					lastVariation = q("body", "html")	
					scrapeProduct(prod)

					if prod.accessoriesLinks is not None \
						and len(prod.accessoriesLinks) > 0:
						for j in range(len(prod.accessoriesLinks)):
							loadProductPage(prod.accessoriesLinks[j].encode("utf-8"))
							scrapeAccessorie(prod)
							driver.back()

					if prod.consumablesLinks is not None \
						and len(prod.consumablesLinks) > 0:		#if prod has consumables
						for j in range(len(prod.consumablesLinks)):
							loadProductPage(prod.consumablesLinks[j].encode("utf-8"))
							scrapeAccessorie(prod, True)
							driver.back()	

			else:	#if product does not have variations
				scrapeProduct(prod)
				if prod.accessoriesLinks is not None \
					and len(prod.accessoriesLinks) > 0:
					for j in range(len(prod.accessoriesLinks)):
						loadProductPage(prod.accessoriesLinks[j].encode("utf-8"))
						scrapeAccessorie(prod)
						driver.back()
				if prod.consumablesLinks is not None \
					and len(prod.consumablesLinks) > 0:		#if prod has consumables
					for j in range(len(prod.consumablesLinks)):
						loadProductPage(prod.consumablesLinks[j].encode("utf-8"))
						scrapeAccessorie(prod, True)
						driver.back()			

	displayStatus("Done!", 1)
	speak("Crawler finished, exit code 1")
	#driver.close()		
	'''
	except Exception as ex:
		print str(ex)
		speak("Exception raised in main thread.")
		print "Last crawl : " + prod.name + " at " + prod.url
		raise(ex)
	'''
	#scrapeProduct("https://www.festool.ro/Products/Pages/Product-Detail.aspx?pid=561184&name=Ferastrau-circular-TS-75-EBQ")   #-- 8 consumables in new tab :(
	
__init__()	
