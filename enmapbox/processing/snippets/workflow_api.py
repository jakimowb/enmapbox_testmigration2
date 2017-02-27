"""
Reads in an image and a mask and multiply them together.
Assumes that the mask is a single band image.
"""

def example_simple_workflowAPI_a():

    from enmapbox.processing.workflow.types import Image, ImageBlock, Workflow

    # Set up workflow
    class Multiplier(Workflow):
        def apply(self, info):
            # set output data and metadata
            cube = self.inputs.image.cube * self.inputs.mask.cube
            meta = self.inputs.image.meta
            self.outputs.outimage = ImageBlock(cube=cube, meta=meta)
    multiplier = Multiplier()
    multiplier.infiles.image = Image('C:\Work\data\Hymap_Berlin-A_Image')
    multiplier.infiles.mask  = Image('C:\Work\data\Hymap_Berlin-A_Mask')
    multiplier.outfiles.outimage = Image('C:\Work\data\outimage_a')
    multiplier.run()

def example_simple_workflowAPI_b():

    from enmapbox.processing.workflow.types import Image, ImageBlock, Workflow

    # Set up workflow
    def multiplyThem(info, inputs, outputs, inargs, outargs):
        # set output data and metadata
        cube = inputs.image.cube * inputs.mask.cube
        meta = inputs.image.meta
        outputs.outimage = ImageBlock(cube=cube, meta=meta)

    multiplier = Workflow()
    multiplier.infiles.image = Image('C:\Work\data\Hymap_Berlin-A_Image')
    multiplier.infiles.mask  = Image('C:\Work\data\Hymap_Berlin-A_Mask')
    multiplier.outfiles.outimage = Image('C:\Work\data\outimage_b')
    multiplier.run(userFunction=multiplyThem)

def example_simple_workflowAPI_c():

    from enmapbox.processing.workflow.types import Image, ImageBlock, Workflow

    # Set up workflow
    def multiplyThem(info, inputs, outputs, inargs, outargs):
        # set output data and metadata
        cube = inputs.image.cube * inputs.mask.cube
        meta = inputs.image.meta
    multiplier = Workflow()
    multiplier.infiles.image = Image('C:\Work\data\Hymap_Berlin-A_Image')
    multiplier.infiles.mask  = Image('C:\Work\data\Hymap_Berlin-A_Mask')
    multiplier.outfiles.outimage = Image('C:\Work\data\outimage_b')
    multiplier.run(userFunction=multiplyThem)


if __name__ == '__main__':
    example_simple_workflowAPI_a()
    example_simple_workflowAPI_b()

    example_simple_workflowAPI_c()
