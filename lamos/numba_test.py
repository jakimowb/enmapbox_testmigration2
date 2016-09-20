from __future__ import print_function
import numpy
from scipy.optimize import leastsq
import pylab as plt
from numba import jit, vectorize
from numba.types import float32, float64, int16
from hub.timing import tic, toc
from scipy.optimize.minpack import _minpack

def create_data(xysize):
    N = 1000 # number of data points
    t = numpy.linspace(0, 4*numpy.pi, N)
    profile = 3.0*numpy.sin(t+0.001) + 0.5 + numpy.random.randn(N) # create artificial data with noise
    cube = profile.reshape(N, 1, 1) * numpy.ones((1, xysize, xysize))
    return t, cube

@jit()
def fit_predict_cube(t, cube):
    N, lines, samples = cube.shape
    out_cube = numpy.zeros_like(cube)
    for line in range(lines):
        for sample in range(samples):
            profile = cube[:,line,sample]
            precition = fit_predict_profile(t, profile)#, optimize_func)
            out_cube[:,line, sample] = precition

    return out_cube

@jit
def optimize_func(x, t, profile):
    result = x[0] * numpy.sin(t + x[1]) + x[2] - profile
    return result

@jit
def _check_func(thefunc, x0, args, numinputs,
                output_shape=None):
    res = args[0]
    dt = res.dtype
    return numpy.shape(res), dt

@jit
def leastsq(func, x0, args):
    n = len(x0)
    shape, dtype = _check_func(func, x0, args, n)
    m = shape[0]
    Dfun = None
    full_output = 0
    col_deriv = 0
    ftol = 1.49012e-8
    xtol = 1.49012e-8
    gtol = 0.0
    maxfev = 200 * (n + 1)
    epsfcn = numpy.finfo(dtype).eps
    factor = 100
    diag = None

    retval = _minpack._lmdif(func, x0, args, full_output, ftol, xtol,
                             gtol, maxfev, epsfcn, factor, diag)
    return retval[0]

@jit#(nopython=True)
def fit_predict_profile(t, profile):
    guess_mean = numpy.mean(profile)
    guess_std = 3 * numpy.std(profile) / (2 ** 0.5)
    guess_phase = 0

    # Define the function to optimize, in this case, we want to minimize the difference
    # between the actual data and our "guessed" parameters

    # optimize_func = lambda x: x[0] * numpy.sin(t + x[1]) + x[2] - profile


    x0 = [guess_std, guess_phase, guess_mean]
    est_std, est_phase, est_mean = leastsq(func=optimize_func, x0=x0, args=(t, profile))
    # est_std, est_phase, est_mean = x0

    # recreate the fitted curve using the optimized parameters
    prediction = est_std * numpy.sin(t + est_phase) + est_mean

    return prediction

def test_plot():
    t, cube = create_data(xysize=10)
    profile = cube[:,0,0]
    precition = fit_predict_profile(t, profile)#, optimize_func)

    plt.plot(profile, '.')
    plt.plot(precition, label='after fitting')
    plt.legend()
    plt.show()

def test_cube(xysize):

    t, cube = create_data(xysize)
    precition = fit_predict_cube(t, cube)

def test_b(a):

    @jit(nopython=True)
    def nansum(a):
        bands, lines, samples = a.shape
        result = numpy.zeros_like(a[0])
        for b in range(bands):
            for l in range(lines):
                for s in range(samples):
                    v = a[b, l, s]
                    if not numpy.isnan(v):
                        result[l, s] += v
                    result[l, s] += v
        return result

    @jit(nopython=True)
    def polyfit(a):
        bands, lines, samples = a.shape
        x = numpy.arange(bands)
        result = numpy.zeros_like(a)
        for l in range(lines):
            for s in range(samples):
                # get training data
                y = a[:, l, s].flatten()
                valid = numpy.isfinite(y)
                # fit
                coeffs = numpy.polyfit(x[valid], y[valid], deg=5)
                fpoly = numpy.poly1d(coeffs)
                # predict
                prediction = fpoly(x)
                result[:, l, s] += prediction
        return result

    def nansum(a): return numpy.nansum(a, axis=0)

    #s = nansum(a)
    s = polyfit(a)

    #print(s.shape)
    #print(type(s))



if __name__ == '__main__':

    a = numpy.random.rand(114, 300, 300).astype(numpy.float64)
    a[::5] = numpy.nan

    tic()
    #test_cube(xysize=100)
    #test_plot()

    for i in range(100):
        test_b(a)
    toc()

    #jit: 15s
    #numpy: 14s
    #python: 273s