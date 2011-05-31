import json
import sys
import header
import index

__all__ = ['header','index']

def _f(path = './default.dat', mode = 'rb'):
    f = open(path, mode)
    return f


if __name__ == '__main__':
    out = None
    try:
        f = _f('../DJEM.dat')
        f = _f('../NAM_culdesac.dat')
        h = header.load(f)
        out = h.dump()
        i = index.load(f,h)
    except Exception as e:
        out = {'error':str(e)}
    json.dump(out, sys.stdout)
