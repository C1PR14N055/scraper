import urllib2

def internet_on():
    try:
        response = urllib2.urlopen('http://google.com',timeout=2)
        print "on"
    except urllib2.URLError as err: 
    	print "off"


internet_on()    