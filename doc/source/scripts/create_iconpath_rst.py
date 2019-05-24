import os

# source dir (location of conf.py)
basedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
# list of icon dirs relative to basedir
icondirs = ['../../enmapbox/gui/ui/icons/',
            '../../site-packages/qps/ui/icons/',
            'img/icons/']

text = ''
for dir in icondirs:
    for file in os.listdir(os.path.join(basedir, dir)):
        if file.endswith('.svg') or file.endswith('.png'):
            print(file)
            text += '.. |{}| image:: /{}\n   :width: 28px\n'.format(os.path.basename(file)[:-4], os.path.join(dir, file))

# write rst file
rst = open(os.path.join(basedir, 'icon_links.rst'), 'w')
rst.write(text)
rst.close()