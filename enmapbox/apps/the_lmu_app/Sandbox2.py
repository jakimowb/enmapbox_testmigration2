# -*- coding: utf-8 -*-

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

x = [range(10), range(5)]
print x
exit()
y = [1.0,2.0,13.0,18.0,44.0,39.0,22.0,35.0,4.0,5.0]
a = y[1]
b = y[-2]

f = interp1d([2,8], [y[1],y[-2]])
print f(8)

exit()

try:
    import matplotlib.pyplot as plt
    ide = "cmd"
except:
    ide = "pycharm"

# Extract coefficients

cols = ['red', 'green', 'blue']

np.set_printoptions(threshold=np.inf)
arr = np.genfromtxt(r"D:\ECST_III\Processor\Modelle\PROSPECT_N_Matlab\abs_coeffs.csv", dtype=np.float, delimiter=";")
x = arr[:,0]

def plotting(mode):
    if ide == "pycharm": return
    plt.plot(x_full, y_full, mode, color=cols[i])

for i, para in enumerate([6,7,8]):

    y = arr[:,para]

    cspline = interp1d(x, y, kind='cubic')

    x_full = range(400,2501)
    y_full = cspline(x_full)


    if para == 6:
        plotting('-')

    else:
        plotting('--')
        y_full[:700] = y_full[700] # Extrapolate to 400nm (baseline)
        y_full = savgol_filter(y_full, window_length=51, polyorder=2, mode='nearest') # SG-Filter
        y_full[y_full < 0] = min(y)
        plotting('-')

        if ide == "pycharm": print list(y_full)

# for wl in xrange(len(x_full)):
#     print "lambda %inm: %f" % (x_full[wl], y_full[wl])


if not ide == "pycharm":

    plt.legend(['dry matter', 'protein original', 'protein post-proc.', 'cellulose original', 'cellulose post-proc.'], loc='best')
    plt.xlabel('Wavelengths [nm]')
    plt.ylabel(u'Absorption coefficients [cm²/g]')
    plt.ylim([0, 130])
    plt.title('Absorption coefficients of PROSPECT Cp parameters')
    plt.show()

