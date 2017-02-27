from __future__ import print_function

def parse(filename):
    with open(filename) as f:
        text = f.readlines()

    print(text)

if __name__=='__main__':

    filename = 'C:\Work\data\EnMAP_DatenKarl\E_L1B_Berlin_20160716_2\E_L1B_Berlin_20160716_2_header.txt'
    parse(filename)