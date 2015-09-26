#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.web.server import NOT_DONE_YET
from bouser.utils import get_args
from bouser.helpers.plugin_helpers import Dependency, BouserPlugin
from twisted.web.resource import Resource

__author__ = 'viruzzz-kun'
__created__ = '26.09.2015'


class AuxiliaryResource(Resource, BouserPlugin):
    cas = Dependency()

    def render(self, request):
        """
        :type request: bouser.web.request.BouserRequest
        :param request:
        :return:
        """
        # Prefer authentication token passed through arguments
        j = get_args(request)
        token = j.get('token')
        if not token:
            # Fallback to token from cookie
            token = request.getCookie(self.cas.cookie_name)
        if not token:
            request.setResponseCode(401)
            return ''

        def _finish(_, status_code):
            request.setResponseCode(status_code)
            request.write('')
            request.finish()

        self.cas.check_token(token).addCallbacks(_finish, _finish, callbackArgs=(200,), errbackArgs=(401,))
        return NOT_DONE_YET
