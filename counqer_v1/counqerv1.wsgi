activate_this = '/root/main/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/counqer_v1/')

from counqerv1 import app as application
