import os

ENV= os.environ.get('DJANGO_ENV', 'dev') # Valeur par défaut 'dev' si la variable d'environnement n'est pas définie

if ENV == 'prod':
    from .prod import *
else : 
    from .dev import *
