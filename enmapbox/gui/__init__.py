import os, sys, logging, site, re
#package providing gui stuff

DEBUG = True
LOAD_PROCESSING_FRAMEWORK = True

if DEBUG:
    #initiate loggers for all pyfiles
    import pkgutil
    DIR = os.path.dirname(__file__)
    for m, name, ispkg in pkgutil.walk_packages(path=DIR, prefix='enmapbox.gui.'):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        fh = logging.StreamHandler()
        fh_formatter = logging.Formatter('%(levelname)s %(lineno)d:%(filename)s%(module)s %(funcName)s \n\t%(message)s')
        fh.setFormatter(fh_formatter)
        fh.addFilter(logging.Filter(name))
        logger.addHandler(fh)


from enmapbox.gui.utils import DIR_SITEPACKAGES
site.addsitedir(DIR_SITEPACKAGES)
