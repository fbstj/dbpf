import json
from sys import argv, stdin
from io import BufferedIOBase
from struct import Struct
from collections import namedtuple

def isFile(f):
    return isinstance(f, BufferedIOBase)

def isFileEX(f, e='Not a file'):
    if not isFile(f):
        raise Exception('Argument Exception',e)

def seek(f,to,by=0):
    isFileEX(f);
    pos = f.tell()
    f.seek(to,by)
    return pos

def version(major, minor):
    return float(".".join([str(major),str(minor)]))

def nt(name, fields): return namedtuple(name, fields)
def st(string): return Struct(string)
