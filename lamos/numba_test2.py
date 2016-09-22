import numpy
from numba import jit

# jit decorator tells Numba to compile this function.
# The argument types will be inferred by Numba when function is called.

@jit
def sum2d(arr):
    M, N = arr.shape
    result = 0.0
    for i in range(M):
        for j in range(N):
            result += arr[i,j]
    return result

a = numpy.arange(9).reshape(3,3)
print(a)
print(sum2d(a))
