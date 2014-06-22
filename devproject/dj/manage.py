#!/usr/bin/env python
import os
import sys

this_dir = os.path.realpath(os.path.dirname(__file__))
ws_dir = os.path.realpath(os.path.join(this_dir, '../../doc/webservice'))
sys.path.insert(1, os.path.join(ws_dir, 'django'))
sys.path.insert(1, os.path.join(ws_dir, 'tornado'))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dj.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
