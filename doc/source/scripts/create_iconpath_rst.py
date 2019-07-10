from os import listdir
from os.path import basename, abspath, dirname, join as jp


# source dir (location of conf.py)
basedir = jp(dirname(abspath(__file__)), '..')
# list of icon dirs relative to basedir
icondirs = ['../../enmapbox/gui/ui/icons/',
            '../../enmapbox/externals/qps/ui/icons/',
            'img/icons/']

text = ''
for dir in icondirs:
    for file in listdir(jp(basedir, dir)):
        if file.endswith('.svg') or file.endswith('.png'):
            print(file)
            text += '.. |{}| image:: /{}\n   :width: 28px\n'.format(basename(file)[:-4], jp(dir, file))

# write rst file
rst = open(jp(basedir, 'icon_links.rst'), 'w')
rst.write(text)
rst.close()