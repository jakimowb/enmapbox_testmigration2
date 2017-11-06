# -*- coding: utf-8 -*-

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter

from queue import Queue, Empty
import numpy as np
from scipy.signal import savgol_filter

a = "hallo"
try:
    b = int(a) + 5
except ValueError:
    print "nope"

exit()


window_size = 3
half_window_size = window_size // 2
data = list()
q = Queue()
d = [2.22, 2.22, 5.55, 2.22, 1.11, 0.01, 1.11, 4.44, 9.99, 1.11, 3.33]
for i in d:
    q.put(i)

res = [None]*window_size
while not q.empty():
    element = q.get()
    data.append(element)
    length = len(data)
    npd = np.array(data[length - window_size:])
    if length == window_size:
        # calculate the polynomial fit for elements 0,1,2,3,4
        poly = np.polyfit(range(window_size), data, deg=2)
        p = np.poly1d(poly)
        for poly_i in range(half_window_size):
            res[poly_i] = p(poly_i) # insert the polynomial fits at index 1
        res[(length-1)-half_window_size] = savgol_filter(npd, window_size, 2)[half_window_size] # insert the sav_gol-value at index 2
        poly = np.polyfit(range(window_size - 1, -1, -1), data[-window_size:], deg=2)
        p = np.poly1d(poly)
        for poly_i_end in range(half_window_size):
            res[(window_size-1)-poly_i_end] = p(poly_i_end)
            # res[3] = p(1) # insert the polynomial fits at index 4
            # res[4] = p(0) # insert the polynomial fits at index 5
    elif length > window_size:
        res.append(None) # add another slot in the res-list
        res[(length-1)-half_window_size] = savgol_filter(npd, window_size, 2)[half_window_size] # overwrite poly-value with savgol
        poly = np.polyfit(range(window_size - 1, -1, -1), data[-window_size:], deg=2)
        p = np.poly1d(poly)
        for poly_i_end in range(half_window_size):
            res[-poly_i_end-1] = p(poly_i_end)
        #
        # res[-2] = p(1)
        # res[-1] = p(0)


# # calculate the polynomial fit for the 5 last elements (range runs like [4,3,2,1,0])
# poly = np.polyfit(range(window_size-1, -1, -1), d[-window_size:], deg=2)
# p = np.poly1d(poly)
# res.append(p(1))
# res.append(p(0))

npd = np.array(data)
res2 = savgol_filter(npd, window_size, 2)


diff = res - res2 # in your example you were calculating the wrong diff btw
np.set_printoptions(precision=2)
print('source data ', npd)
print('online res  ', np.array(res))
print('offline res ', res2)
print('error       ', diff.sum())


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

