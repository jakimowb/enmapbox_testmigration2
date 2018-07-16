import os, sys, logging, site, re
#package providing gui stuff

from enmapbox.gui.settings import qtSettingsObj
settings = qtSettingsObj()
DEBUG = settings.value('EMB_DEBUG', False)
LOAD_PROCESSING_FRAMEWORK = settings.value('EMB_LOAD_PF', True)
LOAD_EXTERNAL_APPS = settings.value('EMB_LOAD_EA', True)
LOAD_INTERNAL_APPS = settings.value('EMB_LOAD_IA', True)



from enmapbox.gui.utils import DIR_SITEPACKAGES
site.addsitedir(DIR_SITEPACKAGES)
