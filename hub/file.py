__author__ = 'janzandr'
import os, fnmatch, json, pickle, hub.collections, numpy, hub.file, sys

def filesearch(dir, pattern):
    files = []
    for root, dirnames, filenames in os.walk(dir):
        for filename in fnmatch.filter(filenames, pattern):
           files.append(os.path.join(root, filename))
    return files

#def dirsearch(dir, pattern):
#    dirs = []
#    for root, dirnames, filenames in os.walk(dir):
#        for dirname in fnmatch.filter(dirnames, pattern):
#           dirs.append(os.path.join(root, dirname))
#    return dirs

def remove(file):
    if os.path.exists(file):
        os.remove(file)
    #try: os.remove(file)
    #except: pass

def mkdir(dir):
    try: os.makedirs(dir)
    except: pass

def mkfiledir(file):
    mkdir(os.path.dirname(file))

def saveJSON(var, file):

    hub.file.mkfiledir(file)
    with open(file, 'w') as file:
        json.dump(var, file)
        #json.dump(var, file, default=json_util.default, indent=4, sort_keys=False)

def restoreJSON(file):
    with open(file, 'r') as file: var = json.load(file)
    return hub.collections.Bunch(var)


def savePickle(var, filename):
    hub.file.mkfiledir(filename)

    #with open(file, 'wb') as file: pickle.dump(var, file)
    with open(filename, 'wb') as file:
        pickle.dump(obj=var, file=file, protocol=1)

def restorePickle(filename):

    with open(filename, 'rb') as file:
        var = pickle.load(file=file)
    return var

if __name__ == '__main__':
    print(dirsearch(r'D:\work\AR\GeoMultiSens\myRasterDB\tiles\UL_170000_-4040000\landsat', 'L*'))
