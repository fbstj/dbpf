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
	def __init__(self, tid, gid, iid, offset, raw, size=None):
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
		return 0
	def __repr__(self):
		return "T{:X}:G{:X}:I{:X}".format(self.type,self.group,self.instance)

class DBPF:
	@property
	def version(self):
		"""a real number representing the header version"""
		return version(self.header[1], self.header[2])

	@property
	def user_version(self):
		"""a real number representing the user version"""
		return version(self.header[3], self.header[4])

	@property
	def index(self):
		"""the table of files in this DBPF"""
		iv = self.header[8] if self.header[1] == 1 else self.header[15]
		return Index(iv, self.header[9], self.header[10], self.header[11])

	@property
	def holes(self):
		"""the table of holes in this DBPF"""
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
		self._scan_dir()

	@property
	def _index_width(self):
		"""the width of records in the index table"""
		return {7.0:5, 7.1:6}.get(self.index.version, '')

	def _scan_records(self):
		"""parse the records table into self.records"""
		ind = self.index
		for rec in self._table(ind.offset, ind.size, self._index_width):
			self.records.append(Record(
				tid = rec[0], gid = rec[1], iid = rec[2],
				offset = rec[-2], raw = rec[-1]
			))

	@property
	def _dir_width(self):
		"""the width of records in the directory table"""
		return {7.0:4, 7.1:5}.get(self.index.version, '')

	def _scan_dir(self):
		"""parse the directory table, appending size variables to appropriate record"""
		dirs = self.search(tid = DIR)
		if len(dirs) == 0:
			return
		if len(dirs) != 1:
			raise DBPFException('multiple directory files')
		d = dirs[0]
		for rec in self._table(d.offset, d.raw, self._dir_width):
			res = self.search(tid = rec[0], gid = rec[1], iid = rec[2])
			res[0].size = rec[-1]

	def _table(self, offset, length, width):
		"""parse the passed """
		self._fd.seek(offset)
		raw = array.array('L',self._fd.read(length));
		for i in range(0, len(raw), width):
			yield list(raw[i : i + width])

	def _read(self, tgi=None, **kwargs):
		"""read the passed file"""
		if tgi is None: tgi = TGI(**kwargs)
		for rec in self.search(tgi):
			self._fd.seek(rec.offset)
			yield self._fd.read(rec.raw)

	def search(self, tgi=None, **kwargs):
		"""search through records for the passed TGI"""
		if tgi is None: tgi = TGI(**kwargs)
		return [f for f in self.records if f.__cmp__(tgi) == 0]

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
