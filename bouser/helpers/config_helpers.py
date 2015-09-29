# -*- coding: utf-8 -*-
from ConfigParser import ConfigParser
import os
from bouser.utils import safe_int

__author__ = 'viruzzz-kun'


def set_value(d, path, items):
    if not path:
        raise Exception('WTF')
    while len(path) > 1:
        key, path = path[0], path[1:]
        if key not in d:
            d[key] = {}
        d = d[key]
    key = path[0]
    if key not in d:
        d[key] = {}
    d[key].update((k, safe_int(v)) for k, v in items)
    return


def parse_config(fp):
    cp = ConfigParser()
    cp.readfp(fp)
    result = {}
    for section in cp.sections():
        path = section.split(':')
        set_value(result, path, cp.items(section))
    return result


def make_config(filename, fmt=None):
    config = {}
    if fmt is None:
        _, ext = os.path.splitext(os.path.basename(filename))
        ext = ext[1:]
        if ext.lower() in ('yaml', 'yml'):
            fmt = 'yaml'
        else:
            fmt = 'conf'
    if fmt == 'yaml':
        import yaml
        with open(filename, 'rb') as cfg_file:
            config.update(yaml.load(cfg_file))
    else:
        with open(filename, 'rt') as cfg_file:
            config.update(parse_config(cfg_file))
    return config
