"""Adhocracy frontent customization for Mercator."""
from pyramid.config import Configurator


def includeme(config):
    """Setup adhocracy frontend extension."""
    # include adhocracy_frontend
    config.include('adhocracy_frontend')
    # override static javascript and css files
    config.override_asset(to_override='adhocracy_frontend:static/',
                          override_with='mercator:static/')


def main(global_config, **settings):
    """ Return a Pyramid WSGI application. """
    config = Configurator(settings=settings)
    includeme(config)
    app = config.make_wsgi_app()
    return app
