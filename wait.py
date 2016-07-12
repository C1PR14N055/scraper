#!/bin/python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

import time

driver = None
USE_FIREFOX = False


def scrape():
	global driver
	url = "https://www.festool.ro/Products/Pages/Product-Detail.aspx?pid=564636&name=Fer-str-u-circular-manual-cu-acumulator-HKC-55-EB-Li-Basic"
	driver.get(url)
	driver.execute_script("__doPostBack('ctl00$PlaceHolderMain$ctl34$LbtnAllSystemAccessories',''); console.log('Going to prod page')")
	try:
		elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#ctl00_PlaceHolderMain_ctl34_ctl00 > div > div:nth-child(14)")))
	except TimeoutException:
		print "We're running out of time... :("
	
	print elem.text


def __init__():
	global driver
	if (USE_FIREFOX):
		binary = FirefoxBinary('/usr/bin/firefox') 
		driver = webdriver.Firefox(firefox_binary=binary) 
	else:	
		driver = webdriver.Chrome("/opt/google/chrome/chromedriver")

	scrape()	



__init__()		