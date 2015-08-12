"""
    ulmo
    ~~~~

    an open source library for clean, simple and fast access to public hydrology and climatology data
"""
from __future__ import absolute_import

from .version import __version__

from .core.api import list_providers, list_services, load_service