# This solution was adopted from code provided by Daniel Scheffler (Developer of EnPT App for EnMAP-Box)

from queue import Queue
from subprocess import Popen
from threading import Thread

def runCmd(cmd, **kwargs):

    def reader(pipe, queue):
        try:
            with pipe:
                for line in iter(pipe.readline, b''):
                    queue.put((pipe, line))
        finally:
            queue.put(None)

    process = Popen(cmd, stdout=-1, stderr=-1, shell=True, **kwargs)
    q = Queue()
    Thread(target=reader, args=[process.stdout, q]).start()
    Thread(target=reader, args=[process.stderr, q]).start()

    for source, line in iter(q.get, None):
        linestr = line.decode('latin-1').rstrip()
        if source.name == 3:
            print(linestr)
        if source.name == 4:
            print(linestr)

    exitcode = process.poll()

    return exitcode
