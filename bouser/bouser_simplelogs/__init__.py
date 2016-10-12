#!/usr/bin/env python
# -*- coding: utf-8 -*-
from . import service
from observer import SimplelogsLogObserver


def make(config):
    SimplelogsLogObserver.set_url(config['url'])
    # return object which will be the application module.
    # Normally this should be a service, that suggests some functionality.
    return service.SimplelogsService()
