import struct
import array
from collections import namedtuple

class Index(namedtuple("DBPF_Index", 'version count offset size')): pass
class Record(namedtuple("DBPF_Record", 'type group instance offset length size raw')): pass

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
		self._scan_records()
		self._scan_dir()
		self._push_raw()

	@property
	def _index_width(self):
		"""the width of records in the index table"""
		return {7.0:5, 7.1:6}.get(self.index.version, '')

	def _scan_records(self):
		"""parse the records table into self.records"""
		ind = self.index
		for rec in self._table(ind.offset, ind.size, self._index_width):
			sql.add_index(rec[0], rec[1], rec[2], rec[-2], rec[-1])

	@property
	def _dir_width(self):
		"""the width of records in the directory table"""
		return {7.0:4, 7.1:5}.get(self.index.version, '')

	def _scan_dir(self):
		"""parse the directory table, appending size variables to appropriate record"""
		dirs = sql.search(DIR)
		if len(dirs) == 0:
			return
		if len(dirs) != 1:
			raise DBPFException('multiple directory files')
		d = Record(*dirs[0])
		for rec in self._table(d.offset, d.length, self._dir_width):
			res = sql.search(rec[0], rec[1], rec[2])
			sql.add_size(rec[0],rec[1],rec[2],rec[-1])

	def _push_raw(self):
		for rec in self.records:
			self._fd.seek(rec.offset)
			sql.add_raw(rec[0],rec[1],rec[2], self._fd.read(rec.length))

	def _table(self, offset, length, width):
		"""parse the passed """
		self._fd.seek(offset)
		raw = array.array('L',self._fd.read(length));
		for i in range(0, len(raw), width):
			yield list(raw[i : i + width])

	@property
	def records(self):
		sql.c.execute("SELECT * FROM files")
		return [Record(*rec) for rec in sql.c.fetchall()]

	def search(self, tid=None, gid=None, iid=None):
		return [Record(*rec) for rec in sql.search(tid,gid,iid)]

DIR = 'E86B1EEF'
EFFDIR = 'EA5118B0'

def RUL(iid=None):
	return ('A5BCF4B', 'AA5BCF57', iid)

#util
def version(major, minor): return float('.'.join([str(major),str(minor)]))

#exceptions
class ArgumentException(Exception): pass
class DBPFException(Exception): pass

if __name__ == '__main__':
	import sql
	import sys
	db = DBPF(sys.argv[1])
	for r in db.search(3899334383L):
		print r
