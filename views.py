from django.http import HttpResponse
from curia.shortcuts import *

# kummelbyvagen -> sergels torg
# latitude_source=17965715&longitude_source=59416341&latitude_destination=18064485&longitude_destination=59332795

def index(request):
    return render_to_response(request, 'kodare.html', {})


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

def spotify_playlist_length(request):
    if request.POST:
        import requests
        import xml.etree.ElementTree as ET

        length = 0.0
        for line in request.POST['data'].split('\n'):
            line = line.replace('http://open.spotify.com/track/', '').strip()
            r = requests.get('http://ws.spotify.com/lookup/1/', params={'uri':'spotify:track:%s' % line})
            if r.content:
                root = ET.fromstring(r.content)
                length += float([x.text for x in root.findall('{http://www.spotify.com/ns/music/1}length')][0])
            else:
                print "couldn't get info for ", line
        return HttpResponse('%d hours %d minutes %d seconds' % (length//(60*60), (length//60)%60, length%60))

    return render_to_response(request, 'spotify_playlist_length.html', {})

def error_test(request):
    asd()