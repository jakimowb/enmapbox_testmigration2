import time
from os.path import join, dirname
from os import makedirs

if 0: # run on desktop
    from hubee.core import ee
    ee.Initialize()

else: # run on ee server
    import ee
    ee.Initialize()

#    f = ee.ApiFunction._api['Image.normalizedDifference']
#    print()

def run2():

    imageCollection = (ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
                              .filter(ee.Filter.eq('WRS_PATH', 193)).filter(ee.Filter.eq('WRS_ROW', 23)).filterDate('2017-01-01', '2018-01-01')
                       )
    image = imageCollection.first().normalizedDifference()
    #image = image.multiply(image2=image) #.multiply(image2=image).normalizedDifference()
    #image = ee.Image.cat(image, image)


    imageInfo = image.getInfo()
    collectionInfo = imageCollection.getInfo()

    return


def createTestData():

    imageCollection = (ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
                       .filter(ee.Filter.eq('WRS_PATH', 194)) # 193 und 194
                       .filter(ee.Filter.eq('WRS_ROW', 23))
                       .filterDate('2017-01-01', '2018-01-01')
                       )

    collectionList = imageCollection.toList(imageCollection.size())
    collectionSize = collectionList.size().getInfo()

    for i in range(collectionSize):
        image = ee.Image(collectionList.get(i))
        info = image.getInfo()
        print(info['id'], image.getDownloadURL(params={'scale': 900}))

        filename = r'C:\Users\janzandr\Downloads\{}\info.json'.format(info['id'])
        try:
            makedirs(dirname(filename))
        except:
            pass

        import json
        with open(filename, 'w') as f:
            json.dump(info, f)

        print(info)


def run():

    def maskL8sr(image):
        # Bits 3 and 5 are cloud shadow and cloud, respectively.
        fillBitMask = (1 << 0)
        cloudShadowBitMask = (1 << 3)
        cloudsBitMask = (1 << 5)
        # Get the pixel QA band.
        qa = image.select('pixel_qa')
        # Both flags should be set to zero, indicating clear conditions.
        mask = (qa
                  .bitwiseAnd(fillBitMask).eq(0)
                  .And(qa.bitwiseAnd(cloudShadowBitMask).eq(0))
                  .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
                )

        masked = image.updateMask(mask)
        return masked

    image193 = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_193023_20170602')
    #image193 = maskL8sr(image193).select(['B5', 'B6', 'B4'])

    image194 = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_194023_20170321')
    #image194 = maskL8sr(image194).select(['B5', 'B6', 'B4'])


    images = (ee.ImageCollection([image193, image194])
                    .map(maskL8sr)
                    .select(['B5', 'B6', 'B4'])

              )

    median = images.reduce(ee.Reducer.median())
    info = median.getInfo()

    kwds = {'region': ee.Geometry.Rectangle(10, 52, 15.5, 54.5)._coordinates,
            'scale': 900,
            'crs': 'EPSG:4326',
            'shardSize': 256,
            'fileDimensions': 256,
            'folder': 'ee_export',
            'noDataValues': [-9999] * 9 + [1] * 3}

    task = ee.batch.Export.image.toDrive(image=median, description='medianX2', **kwds)
#    task.start()

    #task = ee.batch.Export.image.toDrive(image=image193, description='image193', **kwds)
    #task.start()

    #task = ee.batch.Export.image.toDrive(image=image194, description='image194', **kwds)
    #task.start()
    print('done')
    #return

    #image194 = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_194023_20170321')
    #image194 = maskL8sr(image194).select(['B5', 'B6', 'B4'])
    #image194 = image194.select(['B5', 'B6', 'B4'])
    #image = image193.add(image194)
    #image = ee.ImageCollection([image193, image194]).mean()


    #task = ee.batch.Export.image.toDrive(image=image, scale=900, folder='ee_export', description='mean')

    # show progress
    print('Task STARTED')
    task.start()
    while task.active():
        print('*', end='', flush=True)
        time.sleep(1)

    status = task.status()
    print('\nTask {}'.format(status['state']))
    for key in ['output_url', 'error_message']:
        if key in status:
            print(status[key])

    from hubdc.core import openRasterDataset
    #openRasterDataset(filename=status['output_url'][0]).plotMultibandColor(rgbvmin=0, rgbvmax=3000)
    #ds = openRasterDataset(filename=status['output_url'][0])
    #print(ds.readAsArray().min())
    #print(ds.readAsArray().max())

    #ds.plotMultibandColor(rgbvmin=0, rgbvmax=1)
    #ds.plotMultibandColor(rgbvmin=0, rgbvmax=3000)

#weiter: maske korrekt, wird aber nicht richtig angewendet!!!!!!!
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

run()
