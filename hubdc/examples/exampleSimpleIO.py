from hubdc import PixelGrid, Applier, ApplierOperator

def script(i):

    grid = PixelGrid(projection='EPSG:3035', xRes=100, yRes=100, xMin=4400000, xMax=4440000, yMin=3150000, yMax=3200000)
    applier = Applier(grid=grid, nworker=2, nwriter=1, windowxsize=256, windowysize=256)
    applier.setInput('in', filename=r'C:\Work\data\gms\landsat\194\024\LC81940242015235LGN00\LC81940242015235LGN00_cfmask.img')
    applier.setOutput('out', filename=r'c:\output\out'+str(i)+'.tif', format='GTiff')
    applier.run(ufuncClass=SimpleIO)

class SimpleIO(ApplierOperator):

    def ufunc(self):
        self.setData('out', array=self.getData('in'))

if __name__ == '__main__':
    from multiprocessing.pool import ThreadPool, Pool

    pool = ThreadPool(5)
    for i in range(10):
        pool.apply_async(func=script, args=(i,))

    pool.close()
    pool.join()
    print('done ThreadingPool')