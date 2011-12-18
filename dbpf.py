import struct
import json
from sys import argv, stdin
from collections import namedtuple

_h = struct.Struct("4s17i24s")

def _file(f): return isinstance(f,file)
def _efile(f, e='Not a file'):
    if not _file(f): raise Exception(e)

def _seek(f,to,by=0):
    _efile(f);
    pos = f.tell()
    f.seek(to,by)
    return pos

def _version(major, minor):
    return float(".".join([str(major),str(minor)]))




if __name__ == '__main__':
    try:
        print json.dumps({})
    except Exception as e:
        print json.dumps({'error':str(e)})

