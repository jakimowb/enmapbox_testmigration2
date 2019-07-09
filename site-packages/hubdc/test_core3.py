import ee
import hubdc.core3 as ee_
import ee.batch
#ee.batch.Export.image

ee.Initialize()

#ee.FeatureCollection

def Image_ImageOverview():

    id = 'LANDSAT/LC08/C01/T1_TOA/LC08_044034_20140318'
    id_ = r'C:\Users\janzandr\Downloads\LC08_044034_20140318'

    image = ee.Image(id).select(0, 'B2')
    return
    image_ = ee_.Image(id_).select(0, 'B2')

#    imageInfo = image.getInfo()
    imageInfo_ = image_.getInfo()

#    print(image.getInfo())
    print(image_.getInfo())

    print(traverse(image))

#    print(image.getDownloadURL(params={'scale':300}))


'''
    # Concatenate two images into one multi-band image.
    image2 = ee.Image(2)
    image3 = ee.Image.cat([image1, image2])
    print(image3.getInfo())

    # Create a multi-band image from a list of constants.
    multiband = ee.Image([1, 2, 3])
    print(multiband.getInfo())

    # Select and (optionally) rename bands.
    renamed = multiband.select(
        ['constant', 'constant_1', 'constant_2'], # old names
        ['band1', 'band2', 'band3']               # new names
    )
    print(renamed.getInfo())

    # Add bands to an image.
    image4 = image3.addBands(ee.Image(42))
    print(image4.getInfo())
'''

def traverse(obj, indent=0):

    if not hasattr(obj, 'func'):
        print(obj)
        return

    if obj.func is None:
        print(str(obj).replace('\n',''))
        return

    #print('{}{}({})'.format(' ' * indent * 0, obj.func._signature['name'], ', '.join([arg['name'] for arg in obj.func._signature['args']])))
    print('{}{}({})'.format(' ' * indent * 0, obj.func._signature['name'], ', '.join(obj.args.keys())))

    for name in obj.args:
        print('{}{}: '.format(' '*(indent+1)*4, name), end='')
        traverse(obj.args[name], indent+1)
        if not hasattr(obj, 'func'):
            print(str(obj.args[name]).replace('\n',''))

Image_ImageOverview()