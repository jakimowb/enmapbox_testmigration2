# -*- coding: utf-8 -*-

a = range(10)
if any(a[i] == 5 for i in range(3)):
    print "yes"