#!/usr/bin/env python
# -*- coding: utf-8 -*-
from twisted.application.service import Service

from bouser.helpers.plugin_helpers import BouserPlugin


class SimplelogsService(Service, BouserPlugin):
    pass
