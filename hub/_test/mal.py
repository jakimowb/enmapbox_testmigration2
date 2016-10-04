from __future__ import print_function
import matplotlib.pyplot as plt
import numpy

X = range(10+1)
ergebnis = [8*x for x in X]

plt.plot(X, ergebnis)
plt.xlabel('x')
plt.ylabel('f(x) = 8*x')
plt.show()

for i in range(10+1):
    print('8 x',i, '= ', i*8)

