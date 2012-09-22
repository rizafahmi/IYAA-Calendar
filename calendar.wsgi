from pyramid.paster import get_app, setup_logging
import site

site.addsitedir('/app/web/virtualenv/pyramidenv/lib/python2.6/site-packages')
ini_path = '/app/web/virtualenv/pyramidenv/IyaaCalendar/production.ini'
setup_logging(ini_path)
application = get_app(ini_path, 'main') 
