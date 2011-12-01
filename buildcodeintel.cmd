#!/usr/bin/python

# Simple script to generate a ".codeintel/config" file parsing the "bin/django"
# script of a buildout directory.
# Adapted from "mkcodeintel.cmd" found at http://www.martinaspeli.net/articles/sublime-text-2-for-zope-and-plone
# Authored by: Mario Orlandi, Silvebullet S.n.c. - 2011 
# Web: http://silverbullet.it

import os.path
import sys

# Sample "bin/python" file (to be parsed):
#     #!/Users/morlandi/src/github/django-invoicer/env/bin/python
#     import sys
#     sys.path[0:0] = [
#         '/Users/morlandi/src/github/django-invoicer/eggs/South-0.7.3-py2.7.egg',
#         ...
#         '/Users/morlandi/src/github/django-invoicer/eggs/setuptools-0.6c12dev_r88846-py2.7.egg',
#         '/Users/morlandi/src/github/django-invoicer/parts/django',
#         '/Users/morlandi/src/github/django-invoicer',
#         ]
#     ...

# Sample ".codeintel/config" file (the output file)
# {
#     "Python": {
#         "python": "/Users/morlandi/src/github/django-invoicer/env/bin/python",
#         "pythonExtraPaths": [
#             '/Users/morlandi/src/github/django-invoicer/eggs/South-0.7.3-py2.7.egg',
#             ...
#             '/Users/morlandi/src/github/django-invoicer/parts/django',
#             '/Users/morlandi/src/github/django-invoicer',
#         ]
#     }
# }


config = """
{
    "Python": {
"""

djangoscript_path = "bin/django"
if not os.path.exists(djangoscript_path):
    djangoscript_path = "bin/django.py"
    if not os.path.exists(djangoscript_path):
        print "Cannot find django script", djangoscript_path
        sys.exit(1)
djangoscript_path = os.path.abspath(djangoscript_path)

inside_extra_paths = False
f = open(djangoscript_path,'r')
for line in f:
    line = line.strip()
    if line.startswith("#!"):
        config += ' '*8 + '"python": "' + line[2:] + '",' + os.linesep
        config += ' '*8 + '"pythonExtraPaths": ['
    else:
        if inside_extra_paths:
            if line.startswith(']'):
                inside_extra_paths = False
            else:
                config += os.linesep + ' '*12 + line
        else:
            if line.startswith('sys.path[0:0]'):
                inside_extra_paths = True

config += """
        ]
    }
}
"""

print config

if not os.path.exists(".codeintel"):
    os.mkdir(".codeintel")
filepath = os.path.join(".codeintel", "config")
open(filepath, "w").write(config)

print 'New file "%s" created.' % filepath
