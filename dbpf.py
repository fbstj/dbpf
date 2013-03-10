import struct
import array
from collections import namedtuple
import sqlite3
import base64

Header = struct.Struct("4s17L24s")
class Index(namedtuple("DBPF_Index", 'version count offset size')): pass
class Record(namedtuple("DBPF_Record", 'type group instance offset length size raw')): pass

def ID(value):
	"""parses valid IDs into integers"""
	if value is None:
		return None
	if isinstance(value, long) or isinstance(value, int):
		return value
	if isinstance(value, str):
		return int(value, 16)
	return None


def TGI(tid=None, gid=None, iid=None):
	"""produce an sql query with optional parameters"""
	where = []
	if tid is not None:
		where.append(("tid=?" , ID(tid)))
	if gid is not None:
		where.append(("gid=?" , ID(gid)))
	if iid is not None:
		where.append(("iid=?" , ID(iid)))
	return " and ".join([a for a,b in where]), [b for a,b in where]

class DBPF:
	"""a database backed DBPF file"""
	@property
	def version(self):
		"""a real number representing the header version"""
		return version(self.header[1], self.header[2])

	@property
	def user_version(self):
		"""a real number representing the user version"""
		return version(self.header[3], self.header[4])

	@property
	def flags(self):
		"""flags"""
		return self.header[5]

	@property
	def ctime(self):
		"""creation time"""
		return self.header[6]

	@property
	def mtime(self):
		"""modification time"""
		return self.header[7]

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
		"""query the database, return all results"""
		self._db.execute(query, args)
		return self._db.fetchall()

	def __init__(self, fd, db=':memory:'):
		if isinstance(fd, str):
			fd = open(fd, 'rb')
		if not isinstance(fd, file):
			raise ArgumentException('File')
		self._fd = fd;

		fd.seek(0)
		self.header = Header.unpack(fd.read(Header.size))
		if self.header[0] != b'DBPF':
			raise DBPFException('Not a DBPF file')

		self._db = sqlite3.connect(db).cursor()
		self._sql("""CREATE TABLE IF NOT EXISTS
			files ( tid, gid, iid, raw, PRIMARY KEY(tid, gid, iid) )""")
		self.__loaded = False

	def load(self):
		"""lazy loading"""
		if self.__loaded:
			return
		self._scan_records()
		self.__loaded = True

	@property
	def _index_width(self):
		"""the width of records in the index table"""
		return {7.0:5, 7.1:6}.get(self.index.version, '')

	def _scan_records(self):
		"""parse the records table into self.records"""
		ind = self.index
		for rec in self._table(ind.offset, ind.size, self._index_width):
			self._fd.seek(rec[-2])
			self[rec] = self._fd.read(rec[-1]);

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

	def _table(self, offset, length, width):
		"""parse the passed """
		self._fd.seek(offset)
		raw = array.array('L',self._fd.read(length));
		for i in range(0, len(raw), width):
			yield list(raw[i : i + width])

	def __iter__(self):
		"""retrieve all TGIs"""
		self.load()
		for r in self._sql("SELECT tid, gid, iid FROM files"):
			yield r

	def search(self, tid=None, gid=None, iid=None):
		"""search for a particular subset of TGIs"""
		self.load()
		where = TGI(tid,gid,iid)
		query = "SELECT tid, gid, iid FROM files WHERE " + where[0]
		return self._sql(query, where[1])

	def save(self, fd):
		"""save files to the passed fd"""
		# prepare
		head = list(self.header)
		ind = []
		o = Header.size
		for r in self:
			f = self[r]
			ind.append(dict(
				tid = r[0], gid = r[1], iid = r[2],
				offset = o, length = len(f),
				raw = f
			))
			o += len(f)
		# <index<count:4><offset:4><size:4>:12>
		head[9] = len(ind)
		head[10] = o
		head[11] = len(ind) * self._index_width * 4
		# zero hole table
		head[12] = head[13] = head[14] = 0
		# save header
		fd.seek(0)
		fd.write(Header.pack(*head))
		# save files
		for r in ind:
			fd.write(r['raw'])
		# save index
		for r in ind:
			rec = [r['tid'], r['gid'], r['iid'], r['offset'], r['length']]
			fd.write(struct.pack("5L", *rec))

	def __setitem__(self, tgi, raw):
		raw = base64.encodestring(raw)
		args = list(tgi[:3])
		if self[args] == None:
			query = "INSERT INTO files(tid, gid, iid, raw) VALUES (?, ? , ?, ?)"
			args.append(raw)
		else:
			query = "UPDATE files SET raw=? WHERE tid=? AND gid=? AND iid=?"
			args.prepend(raw)
		self._sql(query, args)

	def __getitem__(self, tgi):
		query = "SELECT raw FROM files WHERE tid=? AND gid=? AND iid=?"
		result = self._sql(query,tgi)
		if len(result) < 1:
			return None
		return base64.decodestring(result[0][0])

	def __contains__(self, tgi):
		return self.search(*tgi) > 0

DIR = 'E86B1EEF'
EFFDIR = 'EA5118B0'

def RUL(iid=None):
	"""return the TGI for the RUL with passed instance ID"""
	return ('A5BCF4B', 'AA5BCF57', iid)

#util
def version(major, minor): return float('.'.join([str(major),str(minor)]))

#exceptions
class ArgumentException(Exception): pass
class DBPFException(Exception): pass

if __name__ == '__main__':
	import sys
	db = DBPF(sys.argv[1])
	for r in db:
		f = db[r]
		print "T{:08x}G{:08x}I{:08x}".format(*r), len(f)
	db.save(open("test.dat","wb"))
	print "load saved file"
	db = DBPF("test.dat")
	for r in db:
		f = db[r]
		print "T{:08x}G{:08x}I{:08x}".format(*r), len(f)
