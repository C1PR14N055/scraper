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

from pprint import pprint #pretty print json

import os, time, json

admin_url = 'http://www.premium-store.ro/admin/'
admin_usr = 'admin'
admin_pass = '2VxHnFZfCeF6'
auth_token = None

#URLS
insert_prod_url = 'http://www.premium-store.ro/admin/index.php?route=catalog/product/insert'
#URLS

browser = None
once = False


def insert_prod():
    global browser, once
    rootDir = './prod/'
    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        if not once:
            #print('Found directory: %s' % dirName)
            for fname in fileList:
                #print('\t%s' % fname) 
                if fname == "prod.json":
                    print dirName + " >> " + fname
                    with open(dirName + "/" + fname) as data_file:    
                        prod = json.load(data_file)
                    browser.get(insert_prod_url + auth_token)
                    print insert_prod_url + auth_token
                    q_name("product_description[2][name]").send_keys(prod["title"]) # + prod["subtitle"] if len(prod["subtitle"]) > 0 else "")
                    
                    q("#cke_15")[0].click() #ckick source
                    wait_for_presence(".CodeMirror.cm-s-rubyblue.CodeMirror-wrap")
                    q(".CodeMirror.cm-s-rubyblue.CodeMirror-wrap")[0].click()
                    prod_desc = build_desc_html(prod["product_details_title"], prod["product_details"],
                        prod["product_detail_common_attributes_title"], prod["product_detail_common_attributes"],
                        prod["product_detail_primary_uses_title"], prod["product_detail_primary_uses"],
                        prod["product_detail_performance_features_imgs"], prod["product_pdfs_table"], prod["tehnical_data"])
                    #print prod_desc
                    #q(".CodeMirror > div:nth-child(1) > textarea:nth-child(1)")[0].send_keys(prod_desc)
                    exec_s("$('.CodeMirror > div:nth-child(1) > textarea:nth-child(1)').val(\"" + prod_desc + "\")") #inser val in textarea
                    wait_for_presence(".CodeMirror.cm-s-rubyblue.CodeMirror-wrap")
                    q(".CodeMirror.cm-s-rubyblue.CodeMirror-wrap")[0].click() #ckick textarea wrap to notify JS
                    time.sleep(0.5)
                    #q("#cke_15")[0].click() #ckick source
                    
                    q("#tabs a:nth-child(2)")[0].click() #click data tab
                    q("input[name=model]")[0].send_keys(prod["subtitle"]) #model
                    
                    q("input[name=price]")[0].send_keys(prod["price"][0:prod["price"].index(" RON")].replace(".", "").replace(",", ".")) #price

                    exec_s("$(\"select[name='tax_class_id'] option[value='11']\").attr(\"selected\", \"selected\");") #select tax class
                    
                    exec_s("image_upload('image', 'thumb');") #open inamge manager
                    #q("#top a")[0].click()
                    exec_s("$(\"input[name=\'image\']\").val(\"data/prod" + prod["img"][prod["img"].rindex("/"):] + "\")") #set image

                    q("#tabs a:nth-child(3)")[0].click() #click links tab
                    q("input[name=category]")[0].send_keys("New") #model
                    wait_for_presence("ul.ui-autocomplete li.ui-menu-item a.ui-corner-all")
                    q("input[name=category]")[0].send_keys(Keys.ARROW_DOWN) #model
                    q("input[name=category]")[0].send_keys(Keys.RETURN) #model
                    time.sleep(0.5)
                    q(".buttons a:first-child")[0].click() #save prod
                    #once = True

def build_desc_html(desc_title, desc, common_attr_title, common_attr, 
    uses_title, uses, perf_imgs, pdfs_table, tehn_data):
    
    html = "<div id='prod_desc_block'>"
    if desc_title is not None and desc_title != "": 
        html += "<h3 class='desc_title'>" + desc_title + "</h3>"
    if desc is not None and desc != "":    
        html += "<p class='desc'>" + desc + "</p>"
    if common_attr_title is not None and common_attr_title != "":    
        html += "<h4 class='common_attr_title'>" + common_attr_title + "</h4>"
    if common_attr is not None and common_attr != "":    
        html += "<p class='common_attr'>" + common_attr + "<p>"
    if uses_title is not None and uses_title != "":
        html += "<h4 class='uses_title'>" + uses_title + "</h4>"
    if uses is not None and uses != "":
        html += "<p class='uses'>" + uses + "</p>"
    if perf_imgs is not None and len(perf_imgs) > 0:
        html += "<div class='perf_imgs'>"
        for img in perf_imgs:
            html += "<img class='perf_img' alt='perf img' src='/image/assets/" + img[img.rindex("/"):img.rindex("?")] + "' />"
        html += "</div>"
    if pdfs_table is not None and pdfs_table != "":    
        html += "<div class='pdfs_table'>" 
        html += "<h4>Prospecte / Manuale de utilizare</h4>"
        html += "<table>" + pdfs_table.replace("~/_layouts/15/Tts/BasicPortal.Core/Images/", "/image/assets/").replace("\n", "").replace("\t", "") + "</table>"
        html += "</div>"
    if tehn_data is not None and tehn_data != "":    
        html += "<div class='tehn_data'><table>"
        html += tehn_data.replace("\n", "").replace("\t", "")
        html += "</table></div>"
        html += "</div>"
    html = html.strip().replace("\n", "<br/>").replace("\t", "").replace("\"", "'").replace("</table>", "</table><p>&nbsp;</p>")
    return html

def wait_for_presence(selector):
    global browser
    WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))    
    
def exec_s(script):
    global browser
    print "--- EXEC --- "
    print script
    print "--- EXEC --- "
    browser.execute_script(script)

def q(css_sel):
    global browser
    return browser.find_elements_by_css_selector(css_sel)      

def q_name(name_sel):
    global browser
    return browser.find_elements_by_name(name_sel)[0]          

def login():
    global browser
    browser.get(admin_url)
    username = browser.find_elements_by_name("username")[0]
    password = browser.find_elements_by_name("password")[0]
    username.send_keys(admin_usr)
    password.send_keys(admin_pass)
    q("form a.button")[0].click()
    return browser.current_url[browser.current_url.index("&token="):]

def start():
    global browser, auth_token
    browser = webdriver.Firefox()
    auth_token = login()
    #browser.get(insert_prod_url + auth_token)
    #print insert_prod_url + auth_token
    insert_prod()

start()	