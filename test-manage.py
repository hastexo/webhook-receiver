#!/usr/bin/env python
import os
import sys
import contracts

contracts.disable_all()

# Add Open edX common and LMS Django apps to PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__),
                             'edx-platform'))
for directory in ['common', 'lms']:
    sys.path.append(os.path.join(os.path.dirname(__file__),
                                 'edx-platform',
                                 directory,
                                 'djangoapps'))
for lib in ['xmodule', 'dogstats', 'capa', 'calc', 'chem']:
    sys.path.append(os.path.join(os.path.dirname(__file__),
                                 'edx-platform',
                                 'common',
                                 'lib',
                                 lib))

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
