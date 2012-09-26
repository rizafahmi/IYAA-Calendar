from pyramid.config import Configurator
from pyramid.mako_templating import renderer_factory as mako_factory
from pyramid.events import NewRequest

from urlparse import urlparse
import pymongo


class HttpMethodOverrideMiddleware(object):
    '''WSGI middleware for overriding HTTP Request Method for RESTful support
    '''
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if 'POST' == environ['REQUEST_METHOD']:
            override_method = ''

            # First check the "_method" form parameter
            if 'form-urlencoded' in environ['CONTENT_TYPE']:
                from webob import Request
                request = Request(environ)
                override_method = request.str_POST.get('_method', '').upper()

            # If not found, then look for "X-HTTP-Method-Override" header
            if not override_method:
                override_method = environ.get('HTTP_X_HTTP_METHOD_OVERRIDE', '').upper()

            if override_method in ('PUT', 'DELETE', 'OPTIONS', 'PATCH'):
                # Save the original HTTP method
                environ['http_method_override.original_method'] = environ['REQUEST_METHOD']
                # Override HTTP method
                environ['REQUEST_METHOD'] = override_method

        return self.application(environ, start_response)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_renderer('.html', mako_factory)
    config.add_route('get', 'get/{date}')
    config.add_route('get_olympic', 'get_olympic/{date}')
    config.add_route('add', '/add')
    config.add_route('list', '/list')
    config.add_route('home', '/')
    config.add_route('edit', '/edit/{event_id}')
    config.add_route('delete', '/delete/{event_id}')
    config.add_route('medali', '/medali')
    config.scan()

    # MongoDB Setting
    db_url = urlparse(settings['mongo_uri'])
    conn = pymongo.Connection(host=db_url.hostname, port=db_url.port)
    config.registry.settings['db_conn'] = conn

    def add_mongo_db(event):
        settings = event.request.registry.settings
        db = settings['db_conn'][db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)

        event.request.db = db

    config.add_subscriber(add_mongo_db, NewRequest)

    #return HttpMethodOverrideMiddleware(config.make_wsgi_app())
    return config.make_wsgi_app()
