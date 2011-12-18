import struct
import json
from sys import argv, stdin

def is_dbpf(f):
        "Checks if the file passed is a DBPF file"
        h = struct.unpack("4s",f.read(4))
        return h[0] == "DBPF"

def header(fn = 'default.dat'):
        f = open(fn, 'rb')
        h = struct.unpack("4s17i24s", f.read(96))

        def version(major, minor):
                return float(".".join([str(major),str(minor)]))

        if not is_dbpf(f):
                raise Exception("blah")

        header = dict()

        header['version'] = version(h[1],h[2])
        header['userVersion'] = version(h[3],h[4])
        header['flags'] = h[5]
        header['ctime'] = h[6]
        header['mtime'] = h[7]

        index = dict()
        index['version'] = version(h[8],h[15])
        index['count'] = h[9]
        index['offset'] = h[10] if (h[1]==1) else h[16]
        index['size'] = h[11]

        holes = dict()
        holes['count'] = h[12]
        holes['offset'] = h[13]
        holes['size'] = h[14]

        header['index'] = index
        header['holes'] = holes

        return header
        print json.dumps(header)

if __name__ == '__main__':
        try:
                print json.dumps(header(*argv))
        except Exception as e:
                err = dict()
                err['error'] = e.args
                print json.dumps(err)
