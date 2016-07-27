import numpy

def zvalue_from_index(arr, ind):

    assert arr.ndim == 3

    #_, nC, nR = arr.shape
    #idx = nC * nR * ind + nR * numpy.arange(nR)[:, None] + numpy.arange(nC)

    nB, nL, nS = arr.shape
    idx = nS * nL * ind + nS * numpy.arange(nL)[:, None] + numpy.arange(nS)[None, :]


    return numpy.take(arr, idx)


def nanpercentiles(arr, percentiles, copy=True):

    if copy:
        arr = arr.copy()

    # valid (non NaN) observations along the first axis
    valid_obs = numpy.sum(numpy.isfinite(arr), axis=0)
    max_val = numpy.float(1e100)
    arr[numpy.isnan(arr)] = max_val

    # sort - former NaNs will move to the end
    #arg_sorted_arr = numpy.argsort(arr, axis=0)
    #sorted_arr = zvalue_from_index(arr, arg_sorted_arr)
    sorted_arr = numpy.sort(arr, axis=0)

    result = []
    for percentile in percentiles:

        # desired position as well as floor and ceiling of it
        k_arr = (valid_obs - 1) * (percentile / 100.0)
        f_arr = numpy.floor(k_arr).astype(numpy.int32)
        c_arr = numpy.ceil(k_arr).astype(numpy.int32)
        fc_equal_k_mask = f_arr == c_arr

        # linear interpolation (like numpy percentile) takes the fractional part of desired position
        floor_val = zvalue_from_index(arr=sorted_arr, ind=f_arr) * (c_arr - k_arr)
        ceil_val = zvalue_from_index(arr=sorted_arr, ind=c_arr) * (k_arr - f_arr)
        quant_arr = floor_val + ceil_val
        quant_arr[fc_equal_k_mask] = zvalue_from_index(arr=arr, ind=k_arr.astype(numpy.int32))[fc_equal_k_mask]  # if floor == ceiling take floor value

        # fill with Nan if all inputs are Nan
        quant_arr[valid_obs == 0] = numpy.NaN

        result.append(quant_arr[None])

    return result


def nanargpercentiles(arr, percentiles, copy=True):

    if copy:
        arr = arr.copy()

    # valid (non NaN) observations along the first axis
    valid_obs = numpy.sum(numpy.isfinite(arr), axis=0)
    max_val = numpy.float(1e100)
    arr[numpy.isnan(arr)] = max_val

    # sort - former NaNs will move to the end
    argsorted_arr = numpy.argsort(arr, axis=0)

    result = []
    for percentile in percentiles:
        k_arr = ((valid_obs - 1) * (percentile / 100.0)).astype(numpy.int16)
        arg_arr = zvalue_from_index(arr=argsorted_arr, ind=k_arr)
        result.append(arg_arr)

    return result


def test_nanpercentiles(arr):

    scores = nanpercentiles(arr, percentiles=[50])
    print('\nPercentiles 50%')
    print(scores)

def test_nanargpercentiles(arr):

    indices = nanargpercentiles(arr, percentiles=[50])
    print('\nArgPercentiles 50%')
    print(indices)



if __name__ == '__main__':

    arr = numpy.array([[[numpy.NaN, numpy.NaN, 1],
                        [numpy.NaN, 1, 1]],
                       [[numpy.NaN, 2, 2],
                        [2, 2, 2]],
                       [[numpy.NaN, 3, 3],
                        [numpy.NaN, 3, 3]]])

    print('\nArray')
    print(arr)

    #test_nanpercentiles(arr)
    test_nanargpercentiles(arr)
