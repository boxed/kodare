#!/usr/bin/env python
# coding=utf-8
import sys
sys.path += ['/var/www-python/kodare']

import urllib2
from BeautifulSoup import BeautifulSoup, Tag

page = urllib2.urlopen("http://www.sl.se")
soup = BeautifulSoup(page)

result = []
def foo(tag):
    s = unicode(tag.__str__('utf8').strip(), 'utf8', 'ignore')
    if isinstance(tag, Tag):
        for c in tag.contents:
            foo(c)
    elif not s.startswith('<!--'):
        result.append(s)

foo(soup.findAll('div', id='trafficStatus')[0])

sections = u'\n'.join(result).strip().replace(u'\n\n', u'\n').replace(u'\n\n', u'\n').split(u'\n\n')
sections = [x.split(u'\n') for x in sections]
result = []

headers = [
    u'Tunnelbana',
    u'Pendeltåg',
    u'Lokalbana',
    u'Spårvagn',
    u'Bussar',
]

ignore_headers = [
    u'Lokalbana',
    u'Spårvagn',
]

for x in sections:
    if x[0] != u'entry-content-rel':
        result.extend(x)

ignore_list = [
    u'Inga större störningar', 
    u'Övriga linjer: inga större störningar',
    u'Övrigt: inga större störningar',
]

result = [x for x in result if x not in ignore_list]

last_entry = []
data = {}
for x in result:
    if x in headers:
        last_entry = []
        data[x] = last_entry
    else:
        last_entry.append(x)

data = dict([(x, y) for x, y in data.items() if y and x not in ignore_headers])

if not data:
    subject = u':) SL har inga problem idag'
else:
    subject = u':/ SL har lite problem idag'

html_content = ''

for key, values in data.items():
    html_content += u'<h1>%s</h1>' % key
    for v in values:
        html_content += u'%s<br />' % v
        
from django.core.mail import EmailMessage
msg = EmailMessage(subject, html_content, 'robot@killingar.net', ['boxed@killingar.net'])
msg.content_subtype = "html"  # Main content is now text/html
msg.send()