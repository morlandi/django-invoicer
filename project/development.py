
from project.settings import *
DEBUG=True
TEMPLATE_DEBUG=DEBUG

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'invoices.db',                      # Or path to database file if using sqlite3.
#         'USER': '',                      # Not used with sqlite3.
#         'PASSWORD': '',                  # Not used with sqlite3.
#         'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#     }
# }

# "dumb" python SMTP server:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST='localhost'
EMAIL_PORT = 1025

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + ['project.middleware.QueryCountDebugMiddleware',]
MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + ['project.middleware.DebugFooter',]
try:
    import IPython
    from IPython.Debugger import Tracer
    shell = IPython.Shell.IPShell(argv=[])
    ipdb_set_trace = Tracer(colors='Linux')
    import pdb; pdb.set_trace = ipdb_set_trace
except:
    pass

