from django.http import HttpResponse
from curia.shortcuts import *

# kummelbyvagen -> sergels torg
# latitude_source=17965715&longitude_source=59416341&latitude_destination=18064485&longitude_destination=59332795
def very_simple_fixed_header_ajax(request):
    if request.REQUEST['username'] == 'foo@bar.com' and request.REQUEST['password'] == 'pass':
        return HttpResponse('success')
    else:
        return HttpResponse('login failed')

def very_simple_fixed_header(request):
    return render_to_response(request, 'very_simple/fixed_header.html', {})

def index(request):
    return render_to_response(request, 'kodare.html', {})

def SL(request):
    from kodare.SL import *
    latitude, longitude = request.GET['latitude_source'], request.GET['longitude_source']
    
    planner = TravelPlanner()
    planner.set_source(latitude, longitude)
    planner.set_destination(latitude, longitude)
    return HttpResponse(planner.get_path().encode('utf-8'))
    
def transit_stations(request):
    latitude, longitude = request.GET['latitude_source'], request.GET['longitude_source']
    url = r"http://maps.google.com/maps?f=q&source=s_q&output=json&hl=en&geocode=&q=transit+station+loc%%3A+%(longitude)s%%2C%(latitude)s&btnG=Search+Maps&vps=1&jsv=155c&sll=%(longitude)s%%2C%(latitude)s&sspn=0.011856%%2C0.032015&g=%(longitude)s%%2C%(latitude)s" % {'longitude':longitude, 'latitude':latitude}

    from simplejson import *
    import re
    import urllib2

    #f = open('maps', 'r')
    req = urllib2.Request(url, "OK")
    f = urllib2.urlopen(req)

    name_pattern = re.compile(r'name:\"(.*?)\"')
    coordinate_pattern = re.compile(r'latlng\=(.*?)\\x')
    stations = []
    for entry in f.read().replace('\n', '').replace('\r', '').split('{id:"')[1:-1]:
        try:
            name = name_pattern.search(entry).group(1)
            coordinate = coordinate_pattern.search(entry).group(1).rsplit(',')[:2]
            stations = [name, coordinate[0], coordinate[1]]
        except:
            #print entry
            pass

    f.close()
    return HttpResponse()

def syntax_highlight(request):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter

    if request.POST:
        code = request.POST['code']
        #result = '<style>'+HtmlFormatter().get_style_defs('')+'</style>'
        result = highlight(code, PythonLexer(), HtmlFormatter())
        return HttpResponse(result.encode('utf-8'), mimetype='text/plain')
    return HttpResponse('<html><head><title>Syntax highlight</title></head><body><h1>Syntax highlight code as HTML</h1><form method="post"><textarea cols="70" rows="30" name="code"></textarea><br /><input type="submit" /></form></body></html>')

def objc_to_python_source(request):
    import inspect
    import objc_to_python as m
    return HttpResponse(inspect.getsource(m), mimetype='text/plain')
    
    
def objc_to_python(request):
    from objc_to_python import objc_to_python as convert
    
    if request.POST:
        code = request.POST['code']
        return HttpResponse(convert(code).encode('utf-8'), mimetype='text/plain')
    return HttpResponse('<html><head><title>Objective-C to Python</title></head><body><h1>Convert Objective-C to Python</h1>This will only support some very trivial Objective-C code, Caveat emptor!<br /><form method="post"><textarea cols="70" rows="30" name="code"></textarea><br /><input type="submit" /></form></body></html>')    
    
def sk_forum_planning_calendar(request):
    from datetime import datetime, date
    from icalendar import Calendar, Event, UTC, LocalTimezone # timezone
    cal = Calendar()
    cal.add('prodid', '-//SK Forum Calendar//killingar.net//')
    cal.add('version', '2.0')
    
    import MySQLdb
    connection = MySQLdb.connect(user='root', passwd='2oVGx8VwuqUfY', db='forum')
    cursor = connection.cursor()
    from django.utils.encoding import smart_unicode
    cursor.execute(u'SELECT id FROM users where name = "%s"' % (smart_unicode(request.REQUEST['username'])))
    userID = cursor.fetchall()[0]
    cursor.execute("select id, name, time, description from events, eventdata where events.id = eventdata.event and events.visible = 1 and eventdata.user = %s and eventdata.data in (1, 0)" % userID)
    rows = cursor.fetchall()
    for row in rows:
        id, name, time, description = row
        event = Event()
        event.add('summary', smart_unicode(name.decode('latin-1')))
        #event.add('dtstart', 'DATE:'+time.strftime("%Y%m%d"))
        #event.add('dtend', 'DATE:'+time.strftime("%Y%m%d"))
        event.add('dtstart', date(time.year, time.month, time.day))
        event.add('dtend', date(time.year, time.month, time.day))
        if description:
            event.add('description', smart_unicode(description.decode('latin-1')))
        #event.add('X-FUNAMBOL-ALLDAY', '')
        event['uid'] = 'planning/%s@killingar.net' % id
        event.add('priority', 5) # normal priority
    
        cal.add_component(event)
    connection.close()
    
    return HttpResponse(cal.as_string(), mimetype='text/calendar')