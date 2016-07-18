# -*- coding: utf-8 -*-
from bouser.helpers.plugin_helpers import Dependency
from twisted.web import resource

__author__ = 'viruzzz-kun'


class DefaultRootResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('', RenderedRootResource())


class RenderedRootResource(resource.Resource):
    bouser = Dependency('bouser')

    def render(self, request):
        """
        @type request: bouser.web.request.BouserRequest
        @param request:
        @return:
        """
        request.setHeader('Content-Type', 'text/html; charset=utf-8')
        return request.render_template('root.html', components=self.bouser.modules)


class AutoRedirectResource(resource.Resource):
    def render(self, request):
        """ Redirect to the resource with a trailing slash if it was omitted
        :type request: BouserRequest
        :param request:
        :return:
        """
        request.redirect(request.uri + '/')
        return ""