import os

env = os.getenv('DJANGO_ENV', 'dev')

if env == 'prod':
    from .prod import *
    print("Chargement des settings PROD")
else:
    from .dev import *
    print("Chargement des settings DEV")
