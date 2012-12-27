from pyramid.view import view_config
import datetime
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound


def allowed_methods(*allowed):
    '''Custom predict checking if the HTTP method in the allowed set.
    It also changes the request.method according to "_method" form parameter
    and "X-HTTP-Method-Override" header
    '''
    def predicate(info, request):
        if request.method == 'POST':
            request.method = (
                    request.str_POST.get('_method', '').upper() or
                    request.headers.get('X-HTTP-Method-Override', '').upper() or
                    request.method)

            return request.method in allowed
    return predicate


@view_config(route_name='get',
        request_method='GET',
        accept='json',
        renderer='json')
def get_today(request):
    """docstring for get_today"""
    import json
    from bson import json_util
    if request.matchdict['date'] == 'today':
        tanggal = datetime.datetime.today()
        tgl_no_hour = datetime.datetime(tanggal.year, tanggal.month, tanggal.day, 0, 0, 0)
        last_second = datetime.time.max
        tgl_next = datetime.datetime(tanggal.year, tanggal.month, tanggal.day, last_second.hour, last_second.minute, last_second.second)

    count = request.db['calendar'].find({"tanggal": {"$gte": tgl_no_hour, "$lt": tgl_next}}).sort('_id', -1).count()

    if count > 0:
        data = request.db['calendar'].find({"tanggal": {"$gte": tgl_no_hour, "$lt": tgl_next}}).sort('_id', -1)[0]
    else:
        data = None
    return Response(json.dumps(data, default=json_util.default), headerlist=[('Access-Control-Allow-Origin', '*'), ('Content-Type', 'application/json')])


def get_today_olympic(request):
    """docstring for get_today"""
    import json
    from random import randint
    from bson import json_util

    if request.matchdict['date'] == 'today':
        tanggal = datetime.datetime.today()
        tgl_no_hour = datetime.datetime(tanggal.year, tanggal.month, tanggal.day, 0, 0, 0)
        last_second = datetime.time.max
        tgl_next = datetime.datetime(tanggal.year, tanggal.month, tanggal.day, last_second.hour, last_second.minute, last_second.second)

    #print last_second
    count = request.db['calendar'].find({"tanggal": {"$gte": tgl_no_hour, "$lt": tgl_next}}).count()

    data = request.db['calendar'].find({"tanggal": {"$gte": tgl_no_hour, "$lt": tgl_next}})[randint(0, count)]
    #print data
    #return json.dumps(data, sort_keys=True, indent=4, default=json_util.default)
    print count
    if count > 0:
        return Response(json.dumps(data, default=json_util.default), headerlist=[('Access-Control-Allow-Origin', '*'), ('Content-Type', 'application/json')])


@view_config(route_name='add', renderer='index.html')
def add_view(request):
    import datetime
    import markdown

    if request.POST:
        #print "POST"
        content = markdown.markdown(request.POST['event'])
        content = content.replace('<p>', '')
        content = content.replace('</p>', '')

        tanggal = datetime.datetime.strptime(request.POST['tanggal'], "%d-%m-%Y")
        repeat = datetime.datetime.strptime(request.POST['toDate'], "%d-%m-%Y")
        date_diff = repeat - tanggal
        print date_diff.days

        for repeat in range(int(date_diff.days + 1)):
            tanggal = datetime.datetime.strptime(request.POST['tanggal'], "%d-%m-%Y")
            tanggal = tanggal + datetime.timedelta(days=repeat)

            new_event = {"tanggal": tanggal,
                    "hari": tanggal.strftime("%A"),
                    "agenda": content,
                    "category": "olimpiade"
                    }

            request.db['calendar'].save(new_event)
        url = request.route_url('list')
        return HTTPFound(location=url)
    return {}


@view_config(route_name='list', renderer='list.html')
@view_config(route_name='home', renderer='list.html')
def list_view(request):
    events = request.db['calendar'].find({"category": "olimpiade"}).sort("tanggal", -1)
    return {"events": events}


@view_config(route_name='edit', renderer='edit.html')
def edit_view(request):
    import bson
    import markdown
    import datetime

    pesan = ""

    if request.POST:
        tanggal = datetime.datetime.strptime(request.POST['tanggal'], "%Y-%m-%d %H:%M:%S")
        content = markdown.markdown(request.POST['event'])
        content = content.replace('<p>', '')
        content = content.replace('</p>', '')
        request.db['calendar'].update({"_id": bson.ObjectId(request.matchdict['event_id'])}, {
            "agenda": content,
            "hari": request.POST['hari'],
            "tanggal": tanggal,
            "category": "olimpiade"
            }, save=True)
        pesan = "Saved."

    event = request.db['calendar'].find_one({"_id": bson.ObjectId(request.matchdict['event_id'])})
    return {"event": event, "pesan": pesan}


@view_config(route_name='medali', renderer='medali.html')
def medali_view(request):
    import lxml.html as lh
    import urllib2

    data = []
    url = 'http://ponriau2012.com/'
    doc = lh.parse(urllib2.urlopen(url))
    for elt in doc.iter('tr'):
        kontingen = elt[1].text_content().strip()
    g = elt[2].text_content().strip()
    s = elt[3].text_content().strip()
    b = elt[4].text_content().strip()
    total = elt[5].text_content().strip()
    data.append({'kontingen': kontingen.title(), 'g': g, 's': s, 'b': b, 'total': total})

    return {"data": data[1:8]}


@view_config(route_name='delete')
def delete_view(request):
    import bson
    from pyramid.httpexceptions import HTTPFound

    request.db['calendar'].remove({"_id": bson.ObjectId(request.matchdict['event_id'])})
    return HTTPFound(location=request.route_url('list'))
