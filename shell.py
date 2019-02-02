#!/usr/bin/env python
from accounting import *
from accounting.models import *
from accounting.utils import *
from flask import *

try:
    from IPython import embed
    embed()
except ImportError:
    import os
    import readline
    from pprint import pprint
    os.environ['PYTHONINSPECT'] = 'True'
