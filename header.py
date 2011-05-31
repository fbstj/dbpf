import util
import dbpf


class Header(dbpf.header_type):
    __slots__ = ()

    @property
    def version(self): return util.version(self.versionMajor, self.versionMinor)

    @property
    def user_version(self): return util.version(self.userVersionMajor, self.userVersionMinor)

    @property
    def index(self):
        i = {
            'version':util.version(self.indexVersionMajor,self.indexVersionMinor),
            'count':self.indexCount,
            'offset':self.indexOffset,
            'size':self.indexSize
            }
        return dbpf.header_file2(**i)

    @property
    def holes(self): return dbpf.header_file._make([self.holesCount, self.holesOffset, self.holesSize])

    @property
    def magic(dbpf): return super().magic.decode()

    def dump(self):
        return {
            'version': self.version,
            'userVersion': self.user_version,
            'flags': self.flags,
            'ctime': self.ctime,
            'mtime': self.mtime,
            'index': self.index._asdict(),
            'holes': self.holes._asdict()
            }

def load(file):
    util.isFileEX(file)
    pos = util.seek(file,0)
    _h = dbpf.header_struct
    h = Header._make(_h.unpack(file.read(_h.size)))
    util.seek(file,pos)
    if h.magic != 'DBPF':
        raise dbpf.exception('Not DBPF file')
    return h
