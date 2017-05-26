from hubdc.applier.Writer import Writer

class QueueMock():

    def __init__(self):
        self.outputDatasets = dict()

    def put(self, value):
        task, args = value[0], value[1:]
        Writer.handleTask(task=task, args=args, outputDatasets=self.outputDatasets)
