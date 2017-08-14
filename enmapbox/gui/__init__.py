import os, sys, logging, site, re
#package providing gui stuff

from enmapbox.gui.utils import settings
settings = settings()
DEBUG = settings.value('EMB_DEBUG', True)
LOAD_PROCESSING_FRAMEWORK = settings.value('EMB_LOAD_PF', True)
LOAD_EXTERNAL_APPS = settings.value('EMB_LOAD_EA', True)

if DEBUG:
    #initiate loggers for all pyfiles
    import pkgutil
    DIR = os.path.dirname(__file__)
    for m, name, ispkg in pkgutil.walk_packages(path=DIR, prefix='enmapbox.gui.'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        fh = logging.StreamHandler()
        fh_formatter = logging.Formatter('%(levelname)s %(lineno)d:%(filename)s%(module)s %(funcName)s \n\t%(message)s')
        fh.setFormatter(fh_formatter)
        fh.addFilter(logging.Filter(name))
        logger.addHandler(fh)


from enmapbox.gui.utils import DIR_SITEPACKAGES
site.addsitedir(DIR_SITEPACKAGES)
