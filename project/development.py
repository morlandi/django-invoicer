
from project.settings import *
DEBUG=True
TEMPLATE_DEBUG=DEBUG

# "dumb" python SMTP server:
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST='localhost'
EMAIL_PORT = 1025

MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES) + ['project.middleware.QueryCountDebugMiddleware',]

try:
    import IPython
    from IPython.Debugger import Tracer
    shell = IPython.Shell.IPShell(argv=[])
    ipdb_set_trace = Tracer(colors='Linux')
    import pdb; pdb.set_trace = ipdb_set_trace
except:
    pass

