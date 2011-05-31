import util
import dbpf

class Index(dbpf.tgi):
    pass

def load(file, header):
    util.isFileEX(file) # throw if not a file
    if not isinstance(header, dbpf.header_type):
        raise dbpf.exception('Argument', 'header')
    if header.version != 1:
        raise dbpf.exception("DBPF version not supported", header.version)
    i = header.index
    if i.count < 1:
        return []
    i_width = int(i.size/i.count)
    index = [0]*i.count
    pos = util.seek(file, i.offset)
    for j in range(0,i.count):
        index[j] = dbpf.index(i.version, file.read(i_width))
    pos2 = file.tell()
    if pos2 != (i.offset + i.size): #havent read the right ammount somehow
        raise dbpf.exception("incorrect ammount read", pos2, i.offset, i.size)
    return index
