import struct
import array
from collections import namedtuple

DIR = int('E86B1EEF',16)

def match_parts(parts, a, b):
	if not isinstance(a, dict) or not isinstance(b, dict):
		raise Exception('arguments incorrect')
	for p in parts:
		if a[p] != b[p]:
			return False
	return True

class Header(namedtuple('DBPF_header',[ 'magic',
			'version_major', 'version_minor',
			'user_version_major', 'user_version_minor',
			'flags', 'ctime', 'mtime',
			'index_version_major',
			'index_count', 'index_offset', 'index_size',
			'holes_count', 'holes_offset', 'holes_size',
			'index_version_minor', 'index_offset_v2',
			'unknown', 'reserved',
		])):
	bytes = struct.Struct("4s17i24s")

class Index(namedtuple("DBPF_Index", 'version count offset size')):
	pass

class DBPF:
	@property
	def version(self): return version(self.header[1], self.header[2])

	@property
	def user_version(self): return version(self.header[3], self.header[4])

	@property
	def index(self):
		iv = self.header[8] if self.header[1] == 1 else self.header[15]
		return Index(iv, self.header[9], self.header[10], self.header[11])

	@property
	def holes(self):
		return Index(0, self.header[12], self.header[13], self.header[14])

	def __init__(self, fd):
		if isinstance(fd, str):
			fd = open(fd, 'rb')
		if not isinstance(fd, file):
			raise ArgumentException('File')
		self._fd = fd;
		fd.seek(0)
		_h = Header.bytes
		h = self.header = Header._make(_h.unpack(fd.read(_h.size)))
		if h.magic != b'DBPF':
			raise DBPFException('Not a DBPF file')
		self.records = self._scan_records()

	def _record_bytes(self):
		return struct.Struct({7.0:'5I', 7.1:'6I'}.get(self.index.version, ''))

	def _scan_records(self):
		files = []
		ind = self.index
		# read index
		for id in range(ind.count):
			rb = self._record_bytes()
			self._fd.seek(ind.offset + rb.size * id)
			x = rb.unpack(self._fd.read(rb.size))
			y = dict(
				type = x[0], group = x[1], instance = x[2],
				offset = x[-2],
			)
			self._fd.seek(y['offset'])
			y['raw'] = self._fd.read(x[-1])
			files.append(y)
		# read dir
		directory = []
		for r in files:
			if not r['type'] == DIR:
				continue
			_dir = array.array('i', r['raw'])
			l = 5 if ind.version == 7.1 else 4
			for i in range(0, len(_dir), l):
				_r = list(_dir[i : i + l])
				directory.append(dict( type = _r[0], group = _r[1], instance = _r[2], size = _r[-1]))
			break # only take 1 dir file
		for f in files:
			for d in directory:
				if match_parts(['type','group','instance'], f, d):
					f['size'] = d['size']
		return files

	def search(self, **kwargs):
		for f in self.records:
			if match_parts(kwargs.keys(), kwargs, f):
				yield f

#util
def version(major, minor): return float('.'.join([str(major),str(minor)]))

#exceptions
class ArgumentException(Exception):
	pass

class DBPFException(Exception):
	pass

if __name__ == '__main__':
	import sys
	db = DBPF(sys.argv[1])
	def p(*args): print("{:X}:{:X}:{:X}".format(args[0],args[1],args[2]))
	for f in db.search(type=DIR):
		print f['type'], f['group'], f['instance']
