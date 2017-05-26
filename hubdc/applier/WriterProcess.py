from osgeo import gdal
from multiprocessing import Process, Queue
from time import sleep
from hubdc.applier.Writer import Writer


class WriterProcess(Process):

    def __init__(self):
        Process.__init__(self)
        self.outputDatasets = dict()
        self.queue = Queue()

    def run(self):

        try:
            gdal.SetCacheMax(1)
            while True:

                sleep(0.01) # this should prevent high CPU load during idle time (not sure if this is really needed)
                if self.queue.qsize() == 0:
                    continue
                value = self.queue.get()
                task, args = value[0], value[1:]
                Writer.handleTask(task=task, args=args, outputDatasets=self.outputDatasets)
                if task is Writer.CLOSE_WRITER:
                    break

        except:

            import traceback
            tb = traceback.format_exc()
            print(tb)
