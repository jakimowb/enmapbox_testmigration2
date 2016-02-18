__author__ = 'janzandr'

class Rectangle:
    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

def overlap(rect1, rect2):
    for a, b in [(rect1, rect2), (rect2, rect1)]:
        # Check if a's corners are inside b
        if ((isPointInsideRect(a.left, a.top, b)) or
           (isPointInsideRect(a.left, a.bottom, b)) or
           (isPointInsideRect(a.right, a.top, b)) or
           (isPointInsideRect(a.right, a.bottom, b))):
            return True

    return False

def isPointInsideRect(x, y, rect):
    if (x >= rect.left) and (x <= rect.right) and (y >= rect.top) and (y <= rect.bottom):
        return True
    else:
        return False

if __name__ == '__main__':
    rect1 = Rectangle(0,0,1,-1)
    rect2 = Rectangle(0.5,-0.5,1.5,-1.5)
    rect1 = Rectangle(0,-1,1,0)
    rect2 = Rectangle(0.5,-1.5,1.5,-0.5)



    print(overlap(rect1, rect2))