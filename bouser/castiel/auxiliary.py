#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.web.server import NOT_DONE_YET
from bouser.helpers.plugin_helpers import Dependency, BouserPlugin
from twisted.web.resource import Resource

__author__ = 'viruzzz-kun'
__created__ = '26.09.2015'


class AuxiliaryResource(Resource, BouserPlugin):
    cas = Dependency('bouser.castiel')

    def render(self, request):
        """
        :type request: bouser.web.request.BouserRequest
        :param request:
        :return:
        """
        hex_token = self.__get_hex_token(request)
        if not hex_token:
            request.setResponseCode(401)
            return ''

        def _finish(_, status_code):
            request.setResponseCode(status_code)
            request.write('')
            request.finish()

        self.cas.check_token(hex_token.decode('hex')).addCallbacks(_finish, _finish, callbackArgs=(200,), errbackArgs=(401,))
        return NOT_DONE_YET

    def __get_hex_token(self, request):
        """
        :type request: bouser.web.request.BouserRequest
        :param request:
        :return:
        """
        hex_token = request.all_args.get('token', request.getCookie(self.cas.cookie_name))
        if len(hex_token) != 32:
            raise Exception(u'Bad auth token')
        return hex_token
