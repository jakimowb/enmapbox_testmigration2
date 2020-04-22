# -*- coding: utf-8 -*-
import numpy as np

# Zone Martin:
a = np.asarray([15])
b = a.T
print(a.shape, b.shape)

exit()

water_absorption_bands = [range(959, 1022), range(1390, 1541)]
flat_list = [item for sublist in water_absorption_bands for item in sublist]

print(flat_list)
exit()


w4ter_absorption_bands = list()
last = -2
start = -1

for item in flat_list:
    if item != last+1:
        if start != -1:
            w4ter_absorption_bands.append(range(start, last + 1))
            # p.append([start, last])
        start = item
    last = item

w4ter_absorption_bands.append(range(start, last+1))

print(flat_list)
print(w4ter_absorption_bands)