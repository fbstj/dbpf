import util
import dbpf

def load(file, header):
    util.isFileEX(file) # throw if not a file
    if not isinstance(header, dbpf.header_type):
        raise dbpf.exception('not header')
    if header.version != 1:
        raise dbpf.exception("DBPF version not supported")
    i = header.index
    if i.version == 7.0:
        v = dbpf.index_v0
    else:
        raise dbpf.exception("index version not supported", i.version)
    i_width = int(i.size/i.count)
    index = [0]*i.count
    pos = util.seek(file, i.offset)
    for j in range(0,i.count):
        index[j] = dbpf.index(v,file.read(i_width))
    pos2 = file.tell()
    if pos2 != (i.offset + i.size): #havent read the right ammount somehow
        raise dbpf.exception("incorrect ammount read", pos2, i.offset, i.size)
    return index
