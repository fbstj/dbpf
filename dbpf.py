import struct
import array
from collections import namedtuple
import sqlite3
import base64

class Index(namedtuple("DBPF_Index", 'version count offset size')): pass
class Record(namedtuple("DBPF_Record", 'type group instance offset length size raw')): pass

def ID(value):
	"""parses valid IDs into integers"""
	if value is None:
		return None
	if isinstance(value, long):
		return value
	if isinstance(value, str):
		return int(value, 16)
	return None


def TGI(tid=None, gid=None, iid=None):
	where = []
	if tid is not None:
		where.append(("tid=?" , ID(tid)))
	if gid is not None:
		where.append(("gid=?" , ID(gid)))
	if iid is not None:
		where.append(("iid=?" , ID(iid)))
	return " and ".join([a for a,b in where]), [b for a,b in where]

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
	
	def _sql(self, query, args=[]):
		self._db.execute(query, args)
		return self._db.fetchall()

	def __init__(self, fd, db=':memory:'):
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

		self._db = sqlite3.connect(db).cursor()
		self._sql("""CREATE TABLE IF NOT EXISTS
			files ( tid, gid, iid, raw, PRIMARY KEY(tid, gid, iid) )""")

		self._scan_records()

	@property
	def _index_width(self):
		"""the width of records in the index table"""
		return {7.0:5, 7.1:6}.get(self.index.version, '')

	def _scan_records(self):
		"""parse the records table into self.records"""
		ind = self.index
		for rec in self._table(ind.offset, ind.size, self._index_width):
			tgi = TGI(*rec[:3])
			self._sql("INSERT INTO files(tid, gid, iid) VALUES (?, ? , ?)", tgi[1])
			self._fd.seek(rec[-2])
			raw = self._fd.read(rec[-1])
			args = [base64.encodestring(raw)] + tgi[1]
			self._sql("UPDATE files SET raw=? WHERE tid=? and gid=? and iid=?", args)

		print "index records scanned"

	@property
	def _dir_width(self):
		"""the width of records in the directory table"""
		return {7.0:4, 7.1:5}.get(self.index.version, '')

	def _scan_dir(self):
		"""parse the directory table, appending size variables to appropriate record"""
		dirs = self.search(DIR)
		if len(dirs) == 0:
			return
		if len(dirs) != 1:
			raise DBPFException('multiple directory files')
		d = Record(*dirs[0])
		for rec in self._table(d.offset, d.length, self._dir_width):
			res = sql.search(rec[0], rec[1], rec[2])
			sql.add_size(rec[0],rec[1],rec[2],rec[-1])
		print "directory records scanned"

	def _table(self, offset, length, width):
		"""parse the passed """
		self._fd.seek(offset)
		raw = array.array('L',self._fd.read(length));
		for i in range(0, len(raw), width):
			yield list(raw[i : i + width])

	@property
	def records(self):
		return self._sql("SELECT * FROM files")

	def search(self, tid=None, gid=None, iid=None):
		where = TGI(tid,gid,iid)
		query = "SELECT * FROM files WHERE " + where[0]
		return self._sql(query, where[1])

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
	import sys
	db = DBPF(sys.argv[1])
	for r in db.search(tid=0xA5BCF4B):
		print r[:3]
