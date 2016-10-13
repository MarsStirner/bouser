# -*- coding: utf-8 -*-
import os
import time

from zope.interface import implementer
from bouser.castiel.interfaces import IAuthTokenObject

__author__ = 'viruzzz-kun'


@implementer(IAuthTokenObject)
class AuthTokenObject(object):
    """
    General abstraction of acquired authentication token
    :ivar token: the token itself
    :ivar deadline: unix time of expiration
    :ivar object: object implementing IAuthObject
    """
    __slots__ = ['token', 'deadline', 'object', 'modified']

    def __init__(self, obj, deadline, token=None, modified=None):
        self.token = os.urandom(16) if token is None else token
        self.deadline = deadline
        self.modified = modified or time.time()
        self.object = obj

    @property
    def user_id(self):
        return self.object.user_id
