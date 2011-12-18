import sys
import json
from struct import Struct
from collections import namedtuple
from io import BufferedIOBase

#types
class Header(namedtuple('Header',[ 'magic',
    'version_major', 'version_minor',
    'user_version_major', 'user_version_minor',
    'flags', 'ctime', 'mtime',
    'index_version_major',
    'index_count', 'index_offset', 'index_size',
    'holes_count', 'holes_offset', 'holes_size',
    'index_version_minor', 'index_offset_v2',
    'unknown', 'reserved',
    ])):
    bytes = Struct("4s17i24s")
    Index = namedtuple('Header_Index', 'version count offset size')

    @property
    def version(self): return version(self[1], self[2])

    @property
    def user_version(self): return version(self[3], self[4])

    @property
    def index(self):
        iv = self[8] if self[1] == 1 else self[15]
        return self.Index(iv, self[9], self[10], self[11])

    @property
    def holes(self):
        return self.Index(0, self[12], self[13], self[14])

    @property
    def dir(self):
        for r in self.records():
            if r.tgi.type == 0xE86B1EEF:
                return r
        return None

    def __new__(self, fd):
        if not isinstance(fd, BufferedIOBase):
            raise ArgumentException('File', e)
        self._fd = fd;
        fd.seek(0)
        _h = Header.bytes
        h = Header._make(_h.unpack(fd.read(_h.size)))
        if h.magic != b'DBPF':
            raise DBPFException('Not a DBPF file')
        return h._replace(magic='DBPF')._replace(reserved='')

    def records(self):
        count = self.index.count
        if count < 1:
            raise DBPFException('No records')
        rs = [0]*count
        for i in range(count):
            rs[i] = self.record(i)
        return rs
    
    def record(self, id):
        if self.version_major != 1:
            raise DBPFException('blah')
        i = self.index
        if i.count < id + 1:
            raise DBPFException('Not enough records')
        rb = Record.bytes(self.index.version)
        self._fd.seek(i.offset + rb.size * id)
        return Record._make(rb.unpack(self._fd.read(rb.size)))
        
    def file(self, record):
        if not isinstance(record, Record):
            raise ArgumentException('Record', e)
        _f = record.file
        if not isinstance(_f, Index):
            raise ArgumentException('Index', e)
        self._fd.seek(_f.offset)
        return self._fd.read(_f.size)

    def _asdict(self):
        return {
                'version': self.version, 'user_version': self.user_version,
                'flags': self.flags, 'ctime': self.ctime, 'mtime': self.mtime,
                'index': dict(self.index._asdict()),
                'holes': dict(self.holes._asdict())
            }

TGI = namedtuple('TGI','type group interface')
Index = namedtuple('Index','offset size')

class Record(namedtuple('Record','tgi file')):
    @classmethod
    def _make(cls, iterable):
        return Record(TGI._make(iterable[:3]), Index._make(iterable[-2:]))

    @staticmethod
    def bytes(version):
        return Struct({7.0:'5I', 7.1:'6I'}.get(version, ''))

    def decode(self, blob):
        #parses a binary blob into an object (depending on the TGI)
        pass

    def encode(self, obj):
        #reverses decode on an object (depending on the TGI)
        pass

    def _asdict(self):
        v = dict(self.tgi._asdict())
        v.update(self.file._asdict())
        return v

#util
def version(major, minor): return float('.'.join([str(major),str(minor)]))

#exceptions
class ArgumentException(Exception):
    def __init__(self, *args):
        super().__init__(self,'Argument Exception',*args)

class DBPFException(Exception):
    def __init__(self, *args):
        super().__init__(self,'Argument Exception',*args)

if __name__ == '__main__':

    _f = open('../DJEM.dat', 'rb')
    _h = Header(_f)
    _i = _h.records()
    _r = _h.record(0)
    _b = _h.file(_r)

TypesByID = {
    0xE86B1EEF: 'DIR'
}
