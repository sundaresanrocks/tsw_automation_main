"""
================================
RPM Checks script
================================

Checks the rpm on the target machines

"""


NIGHTLY_INI_FILE = runtime.src_path + '/' + ACTIVE_PROJECT + '/conf/env/nightly.ini'
import os
import runtime
import logging
import copy

from lib.properties.base import PropertiesBase
propobj = PropertiesBase()
propobj.load_config_section(NIGHTLY_INI_FILE, 'General')
HOST = propobj.get_kvpair()