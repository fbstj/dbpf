import util
import dbpf
import header

def load(f, h):
    util.isFileEX(f)
    if not isinstance(h, header.Header):
        raise dbpf.exception('not header')
    if h.version != 1:
        raise dbpf.exception("version not supported")
    i = h.index
    if i.version == 7.0:
        v = dbpf.index_v0
    else:
        raise dbpf.exception("index version not supported", i.version)
    i_width = int(i.size/i.count)
    index = [0]*i.count
    pos = util.seek(f, i.offset)
    for j in range(0,i.count):
        index[j] = dbpf.index(v,f.read(i_width))
    if f.tell() != (i.offset + i.size) :
        raise dbpf.exception("incorrect ammount read", f.tell(), i.offset, i.size)
    return index
