#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime

from twisted.internet import defer
from twisted.web.resource import IResource, Resource
from twisted.web.util import redirectTo
from twisted.logger import Logger
from zope.interface import implementer

from bouser.helpers.plugin_helpers import BouserPlugin, Dependency
from bouser.castiel.exceptions import EExpiredToken, ETokenAlreadyAcquired, EInvalidCredentials
from bouser.web.interfaces import IWebSession
from bouser.bouser_simplelogs import SimplelogsLogObserver


logger = Logger(
    observer=SimplelogsLogObserver(system_name='Coldstar.Castiel'),
    namespace="coldstar.castiel")


__author__ = 'viruzzz-kun'
__created__ = '08.02.2015'


re_referrer_origin = re.compile(u'\Ahttps?://(?P<origin>[\.\w\d]+)(:\d+)?/.*', (re.U | re.I))


def alter_back(back, args, token):
    if 'with_token' in args:
        if '?' in back:
            return back + '&token=%s' % token
        else:
            return back + '?token=%s' % token
    return back


@implementer(IResource)
class CastielLoginResource(Resource, BouserPlugin):
    isLeaf = True

    service = Dependency('bouser.castiel')

    @defer.inlineCallbacks
    def render_GET(self, request):
        """
        :type request: bouser.web.request.BouserRequest
        :param request:
        :return:
        """
        token = request.getCookie(self.service.cookie_name)
        session = request.getSession()
        fm = IWebSession(session)
        if 'back' in request.args:
            fm.back = request.args['back'][0]
        elif not fm.back:
            fm.back = request.getHeader('Referer') or '/'
        try:
            if token:
                token = token.decode('hex')
                yield self.service.check_token(token)
            else:
                defer.returnValue(request.render_template('login.html'))
        except EExpiredToken:
            defer.returnValue(request.render_template('login.html'))
        else:
            # Token is valid - just redirect
            back, fm.back = fm.back, None
            back = alter_back(back, request.args, token.encode('hex'))
            defer.returnValue(redirectTo(back, request))

    @defer.inlineCallbacks
    def render_POST(self, request):
        """
        :type request: bouser.web.request.BouserRequest
        :param request:
        :return:
        """
        session = request.getSession()
        fm = IWebSession(session)
        back = request.args.get('back', [fm.back])[0] or '/'
        try:
            login = request.args['login'][0].decode('utf-8')
            password = request.args['password'][0].decode('utf-8')
            ato = yield self.service.acquire_token(login, password)
            logger.info(u'Пользователь {user_descr} аутентифицировался {dt:%d.%m.%Y %H:%M:%S}',
                        user_descr=ato.object.get_description(), dt=datetime.datetime.now(),
                        tags=['AUTH'])
        except EInvalidCredentials:
            fm.flash_message(dict(
                text=u"Неверное имя пользователя или пароль",
                severity='danger'
            ))
            logger.warn(u'Неудачная попытка аутентификации по логину {login} {dt:%d.%m.%Y %H:%M:%S} '
                        u'(Неверное имя пользователя или пароль)',
                        login=login, dt=datetime.datetime.now(), tags=['AUTH'])
            defer.returnValue(redirectTo(request.uri, request))
        except ETokenAlreadyAcquired:
            fm.back = None
            defer.returnValue(redirectTo(back, request))
        else:
            token_txt = ato.token.encode('hex')

            domain = request.getHeader('Host').split(':', 1)[0]
            uri = request.getHeader('Referer')
            if uri:
                match = re_referrer_origin.match(uri)
                if match:
                    domain = match.groupdict()['origin']

            cookie_domain = self.service.get_cookie_domain(domain)
            request.addCookie(
                str(self.service.cookie_name), token_txt, domain=str(cookie_domain),
                path='/', comment='Castiel Auth Cookie'
            )
            fm.back = None
            back = alter_back(back, request.args, token_txt)
            defer.returnValue(redirectTo(back, request))
