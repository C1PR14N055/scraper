import xml.etree.ElementTree as ET
from pprint import pprint

root = ET.parse('sitemap.xml').getroot()
f = open("sitemap.txt", "w")

for el in root.findall('url'):
	f.write(el.find('loc').text + "\n")

f.close()	

