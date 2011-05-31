import util

class exception(Exception):
    pass

header_type = util.nt('header_type', [
    'magic',
    'versionMajor', 'versionMinor',
    'userVersionMajor', 'userVersionMinor',
    'flags',
    'ctime', 'mtime',
    'indexVersionMajor',
    'indexCount', 'indexOffset', 'indexSize',
    'holesCount', 'holesOffset', 'holesSize',
    'indexVersionMinor',
    'indexOffset2',
    'unknown',
    'reserved',
    ])

header_struct = util.st("4s17i24s")
header_file = util.nt('header_file', 'count offset size')
header_file2 = util.nt('header_file2', ('version',) + header_file._fields)

tgi = util.nt('tgi','type group instance')

index_v0 = 5#[util.nt('index_v0', 't g i o l'), util.st('5I')]
index_v1 = 6#[util.nt('index_v1', 't g i i2 o l'), util.st('6I')]
#index_v3 = util.nt('_v3', '' )

def index(version, string): return util.st(str(version)+'I').unpack(string)
