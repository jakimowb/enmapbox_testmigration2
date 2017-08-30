# -*- coding: utf-8 -*-

class A:
    def __init__(self, class_b):
        self.myVariable = 10
        self.class_b = class_b
        self.class_b.myOtherVariable = 12

class B:
    def __init__(self):
        self.myOtherVariable = 6


if __name__ == '__main__':
    b = B
    a = A(b)

    print (b.myOtherVariable)