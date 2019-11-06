from os import listdir
from os.path import basename, abspath, dirname, join


# source dir (location of conf.py)
basedir = join(dirname(abspath(__file__)), '..')
# list of icon dirs relative to basedir
icondirs = ['../../enmapbox/gui/ui/icons/',
            '../../enmapbox/externals/qps/ui/icons/',
            'img/icons/']
extentions = ('.svg', '.png')

text = ''
for dir in icondirs:
    for file in listdir(join(basedir, dir)):
        if file.endswith(extentions):
            print(file)
            text += '.. |{}| image:: /{}\n   :width: 28px\n'.format(basename(file)[:-4], join(dir, file))

# write rst file
rst = open(join(basedir, 'icon_links.rst'), 'w')
rst.write(text)
rst.close()