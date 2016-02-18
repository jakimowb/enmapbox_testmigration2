import time, sys

def tic(info=''):
    global tictimes, ticinfos
    try:
        tictimes.append(time.clock())
        ticinfos.append(info)
    except:
        tictimes = [time.clock()]
        ticinfos = [info]
    print('start...'+info)
    sys.stdout.flush()

def toc():
    global times
    t1, t2, info = tictimes.pop(), time.clock(), ticinfos.pop()
    print('...done '+info+' in '+str(int(t2 - t1))+' sec | '+str(round((t2 - t1)/60,2))+' min | '+str(round((t2 - t1)/60/60,2))+' hours\n')
    sys.stdout.flush()

def progress(i, n, info=''):
    print(info+' ('+str(i)+'/'+str(n)+')')