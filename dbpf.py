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

def index(version, string):
    s = str({
            7.0:'5I',
            7.1:'6I'
        }.get(version, ''))
    if len(s) == 0:
        raise exception("Version not supported", version)
    return util.st(s).unpack(string)
