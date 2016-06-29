import os, sys, fnmatch, six, subprocess

ROOT = os.path.dirname(__file__)


def file_search(rootdir, wildcard, recursive=False, ignoreCase=False):
    assert rootdir is not None
    if not os.path.isdir(rootdir):
        six.print_("Path is not a directory:{}".format(rootdir), file=sys.stderr)

    results = []

    for root, dirs, files in os.walk(rootdir):
        for file in files:
            if (ignoreCase and fnmatch.fnmatch(file.lower(), wildcard.lower())) \
                    or fnmatch.fnmatch(file, wildcard):
                results.append(os.path.join(root, file))
        if not recursive:
            break
    return results


def make():

    #compile resource files
    resourcefiles = file_search(ROOT, 'resource*.qrc', recursive=True)
    for f in resourcefiles:
        dn = os.path.dirname(f)
        bn = os.path.basename(f)
        bn = os.path.splitext(bn)[0]
        pathPy2 = os.path.join(dn, bn+'_py2.py' )
        pathPy3 = os.path.join(dn, bn+'_py3.py' )
        print('Make {}'.format(pathPy2))
        subprocess.call(['pyrcc4','-py2','-o',pathPy2, f])
        print('Make {}'.format(pathPy3))
        subprocess.call(['pyrcc4','-py3','-o',pathPy3, f])



if __name__ == '__main__':

    make()
    print('Done')

