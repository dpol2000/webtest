# -*- coding: utf-8 -*-

import os
import json
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    """Get the environment variable or return exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)


def get_config():

  #  base_dir = os.path.join( os.path.dirname( __file__ ), '..' )
    base_dir = os.path.join( os.path.dirname ( __file__), os.path.pardir)
    path = os.path.join(base_dir, 'config.json')

    with open(path) as f:
        config = json.loads(f.read())
    return config


def get_config_key(key, config):
    """Get the secret variable or return explicit exception."""

    try:
        return config[key]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(key)
        raise ImproperlyConfigured(error_msg)
