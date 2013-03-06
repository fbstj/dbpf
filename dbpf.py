import struct
import array
from collections import namedtuple

DIR = int('E86B1EEF',16)

class TGI:
	def __init__(self, tid=None, gid=None, iid=None):
		self.type = tid
		self.group = gid
		self.instance = iid
	@staticmethod
	def __fmt(value=None):
		return "?" if value is None else "{:X}".format(value)

	def __repr__(self):
		return "T{:s}:G{:s}:I{:s}".format(
					self.__fmt(self.type),
					self.__fmt(self.group),
					self.__fmt(self.instance)
				)

class Index(namedtuple("DBPF_Index", 'version count offset size')): pass
class Record:
	def __init__(self, tid, gid, iid, offset, raw=None, size=None):
		self.type = tid
		self.group = gid
		self.instance = iid
		self.offset = offset
		self.raw = raw
		self.size = size

	def __cmp__(self, to):
		if not isinstance(to, TGI):
			return 1;
		if to.type is not None:
			if self.type != to.type:
				return 2
		if to.group is not None:
			if self.group != to.group:
				return 3
		if to.instance is not None:
			if self.instance != to.instance:
				return 4
		print self, "==", to
		return 0
	def __repr__(self):
		return "T{:X}:G{:X}:I{:X}".format(self.type,self.group,self.instance)

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
		hb = struct.Struct("4s17i24s")
		self.header = hb.unpack(fd.read(hb.size))
		if self.header[0] != b'DBPF':
			raise DBPFException('Not a DBPF file')
		self.records = []
		self._scan_records()
		for f in self.records
			print f
		self._scan_dir()

	def _record_bytes(self):
		return struct.Struct({7.0:'5I', 7.1:'6I'}.get(self.index.version, ''))

	def _scan_records(self):
		# read index
		rb = self._record_bytes()
		o = self.index.offset
		seek = self._fd.seek
		read = self._fd.read
		for id in range(self.index.count):
			seek(o + rb.size * id)
			x = rb.unpack(read(rb.size))
			seek(x[-2])
			self.records.append(Record(
				tid = x[0], gid = x[1], iid = x[2],
				offset = x[-2], raw = read(x[-1])
			))

	def _scan_dir(self):
		# read dir
		dir_records = self.search(tid = DIR)
		if len(dir_records) != 1:
			raise DBPFException('incorrect DIR records')

		_dir = array.array('i', dir_records[0].raw)
		l = 5 if self.index.version == 7.1 else 4

		for i in range(0, len(_dir), l):
			slice = list(_dir[i : i + l])
			f = self.search(tid = slice[0], gid = slice[1], iid = slice[2])
			print f, slice
			if len(f) != 1:
				raise DBPFException('multiple instances of TGI')
			f[0].size = slice[-1]

	def search(self, **kwargs):
		return [f for f in self.records if f == TGI(**kwargs)]

#util
def version(major, minor): return float('.'.join([str(major),str(minor)]))

#exceptions
class ArgumentException(Exception): pass
class DBPFException(Exception): pass

if __name__ == '__main__':
	import sys
	db = DBPF(sys.argv[1])
	def p(*args): print("{:X}:{:X}:{:X}".format(args[0],args[1],args[2]))
	print db.version, db.user_version, db.index
	for f in db.search(tid=DIR):
		print f['type'], f['group'], f['instance']
