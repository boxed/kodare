# -*- coding: utf-8 -*-
import re
import urllib, urllib2

def substitute_entity(match):
    from htmlentitydefs import name2codepoint as n2cp
    ent = match.group(2)
    if match.group(1) == "#":
        return unichr(int(ent))
    else:
        cp = n2cp.get(ent)

        if cp:
            return unichr(cp)
        else:
            return match.group()

def decode_htmlentities(string):
    entity_re = re.compile("&(#?)(\d{1,5}|\w{1,8});")
    return entity_re.subn(substitute_entity, string)[0]

def clean(s):
	return decode_htmlentities(s.replace('&nbsp;', ' ').replace('<br />', '\n').replace('<p>', '\n\n').replace('</p>', '').replace('<strong>','').replace('</strong>','').strip())

class TravelPlanner:
    def __init__(self):
        self.url = 'http://reseplanerare.sl.se/bin/query.exe/sn'
        self.sequence_and_ident_pattern = re.compile(r'\?seqnr\=(.*?)\&ident\=(.*?)\&')
        self.sequence_and_ident = None
        
        req = urllib2.Request(self.url, "OK")
        response = urllib2.urlopen(req)
        html = response.read()
        self.update_sequence_and_ident(html)

    def update_sequence_and_ident(self, html):
        m = self.sequence_and_ident_pattern.search(html)
        seqnr = int(m.group(1))
        ident = m.group(2)
        self.sequence_and_ident = (seqnr, ident)

    def set_map_coordinates(self, y, x):
        values = {
            'performGis': '1',
            'REQMapCenterCoordType': 'GEO',
            'REQMapCenterX': x, #'17965715',
            'REQMapCenterY': y, #'59416341',
            'REQMapScaling': 1,
        }

        req = urllib2.Request(self.url, urllib.urlencode(values))
        response = urllib2.urlopen(req)
        html = response.read()
        if 'felmeddelande' in html: # Felmeddelande
            print html
            raise 'failed to set map coordinates'
        self.update_sequence_and_ident(html)

    def get_address(self, param):
        values = {   
            'seqnr': self.sequence_and_ident[0],
            'ident': self.sequence_and_ident[1],
            'performGis': '1',
            'REQMapTask': 'MAPINPUT',
            'REQMapClickPixelPosX': '180',
            'REQMapClickPixelPosY': '180',
            'REQMapClickAction': param, #'TAKE_AS_START0', # REQMapClickAction=TAKE_AS_DEST0
            'RemoveGlobalOptionGO_callMapFromPosition': '',
            'setMapLoc': 'from',
        }
        req = urllib2.Request(self.url, urllib.urlencode(values))

        response = urllib2.urlopen(req)
        html = response.read()
        if 'felmeddelande' in html:
            print html
            raise 'failed to get search page'
        self.update_sequence_and_ident(html)
        foo = re.compile(r'<strong>(.*?)</strong')
        return decode_htmlentities(foo.search(html).group(1))

    def get_path(self):
    	import urllib2
    	from BeautifulSoup import BeautifulSoup
    	from urllib import urlencode

    	# S (source)
    	# Z (destination)
    	# start=yes
    	# REQ0HafasSearchForw
    	#	1 for time specified being departure time
    	#	0 for time specified being arrival time
    	# REQ0JourneyDate
    	#	+number of days in the future
    	# REQ0JourneyTime (optional)
    	#	HH:MM or relative time in the format +H:MM

    	depart_time = '+0:05'
    	query = urlencode({
    	    'start':'', 
    	    'REQ0JourneyStopsS0G':self.source, 
    	    'REQ0JourneyStopsZ0G':self.destination, 
    	    'REQ0JourneyStopsSID':'A=1@O='+self.source+'@X='+self.source_x+'@Y='+self.source_y,
    	    'REQ0JourneyStopsZID':'A=1@O='+self.destination+'@X='+self.destination_x+'@Y='+self.destination_y,
    	    'REQ0JourneyStopsS0A':255,
    	    'REQ0JourneyStopsZ0A':255,
    	    'REQ0JourneyTime':depart_time,
    	    }, 1)
    	page = urllib2.urlopen(self.url+'?'+query)
    	soup = BeautifulSoup(page)
    	for hit in soup.findAll('div', {'class':'FormArea2'}):
    		if 'Trevlig resa' in str(hit):
    			return clean(''.join([unicode(x) for x in hit.contents]).replace('Trevlig resa!', '')).replace('<strong>', '').replace('</strong>', '')

    	# no hit!
    	# source suggested alternatives: select with id REQ0JourneyStopsS0K
    	# destination suggested alternatives: select with id REQ0JourneyStopsZ0K

    	return soup
    
    def set_source(self, x, y):
        self.set_map_coordinates(x, y)
        self.source = self.get_address('TAKE_AS_START0')
        self.source_x = x
        self.source_y = y

    def set_destination(self, x, y):
        self.set_map_coordinates(x, y)
        self.destination = self.get_address('TAKE_AS_DEST0')
        self.destination_x = x
        self.destination_y = y

#planner = TravelPlanner()
#planner.set_source('17965715', '59416341')
#planner.set_destination('18064485', '59332795')
#print planner.get_path().encode('utf-8')
# ?seqnr=something&ident=somethingelse&