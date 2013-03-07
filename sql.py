import sqlite3
import base64

con = sqlite3.connect(":memory:")

c = con.cursor()

c.execute("""CREATE TABLE files (
		type_id INT, group_id INT, instance_id INT,
		offset INT, length INT, size INT, raw BLOB,
		PRIMARY KEY(type_id, group_id, instance_id)
	)""")

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
		where.append(("type_id=?" , ID(tid)))
	if gid is not None:
		where.append(("group_id=?" , ID(gid)))
	if iid is not None:
		where.append(("instance_id=?" , ID(iid)))
	return " and ".join([a for a,b in where]), [b for a,b in where]

def search(tid=None, gid=None, iid=None):
	where = TGI(tid,gid,iid)
	query = "SELECT * FROM files WHERE " + where[0]
	c.execute(query, where[1])
	return c.fetchall()

def add_index(tid, gid, iid, offset, length):
	c.execute(""" INSERT INTO files(type_id, group_id, instance_id, offset, length)
						VALUES (?, ? , ?, ?, ?)""", [tid, gid, iid, offset, length])

def add_size(tid, gid, iid, size):
	where = TGI(tid, gid, iid)
	query = "UPDATE files SET size=? WHERE " + where[0]
	c.execute(query, [size] + where[1])

def add_raw(tid, gid, iid, raw):
	where = TGI(tid,gid,iid)
	query = "UPDATE  files SET raw=? WHERE " + where[0]
	c.execute(query, [base64.encodestring(raw)]+where[1])

def get_raw(tid, gid, iid):
	where = TGI(tid,gid,iid)
	query = "SELECT (raw=?) FROM files WHERE " + where[0]
	c.execute(query, [base64.encodestring(raw)]+where[1])
	return c.fetchall()

