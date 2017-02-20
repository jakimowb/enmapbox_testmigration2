from __future__ import absolute_import
from multiprocessing import Pool as ProcessPool
from multiprocessing.pool import ThreadPool

def job(args):
    if len(args) == 2: # function
        methode, kwargs = args
        methode(**kwargs)
    elif len(args) == 3: # obj methode
        self, methode, kwargs = args
        methode(self, **kwargs)
    else:
        raise Exception('wrong usage!')

def run_pool(Pool, argss, processes):

    if processes == 1:
        for args in argss:
            job(args)
    else:
        pool = Pool(processes=processes)
        pool.map(job, argss)